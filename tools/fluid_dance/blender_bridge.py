"""Run with Blender to build an editable skinned rig and bake its evaluation.

blender -b --factory-startup --python tools/fluid_dance/blender_bridge.py -- \
  --input work/fluid-dance/performance/authoring-input.npz \
  --output work/fluid-dance/performance/performance.npz \
  --blend work/fluid-dance/performance/authoring.blend

The source is newly authored native animation, not video-recovered capture.
This first bridge transfers solved controls to editable Blender bone keys;
it does not claim to create a full animator-facing control-rig UI.

Use --from-blend instead of --blend to evaluate a saved, possibly edited
armature without rebuilding its keys or saving over the source .blend.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector


SCHEMA="concert.performance.bundle.v1"
B=Matrix(((1.,0.,0.),(0.,0.,-1.),(0.,1.,0.)))
BI=B.transposed()


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def continuity(q):
    q=np.asarray(q,dtype=np.float64)
    for j in range(1,len(q)):
        dot=np.sum(q[j-1]*q[j],axis=-1,keepdims=True)
        q[j]=np.where(dot<0,-q[j],q[j])
    return q


def create_rest_armature(data, object_name="Fluid Fan Performance"):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    arm_data=bpy.data.armatures.new("Mother's Love native skeleton")
    arm=bpy.data.objects.new(object_name,arm_data)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm;arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    names=[str(s) for s in data["bone_names"]]
    parents=data["parents"]
    for j,name in enumerate(names):
        bone=arm_data.edit_bones.new(name)
        h=B@Vector(data["model_heads"][j]);t=B@Vector(data["model_tails"][j])
        if (t-h).length<1e-6:t=h+Vector((0.,0.,.01))
        bone.head=h;bone.tail=t
        if parents[j]>=0:bone.parent=arm_data.edit_bones[names[parents[j]]]
        bone.use_connect=False
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.show_in_front=True;arm.data.display_type="OCTAHEDRAL"
    for bone in arm.pose.bones:bone.rotation_mode="QUATERNION"
    return arm,names,parents


def build_armature(data):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    arm,names,parents=create_rest_armature(data)
    # The original modelled mesh, not a reskinned neutral approximation.
    if "model_vertices" in data:
        mesh=bpy.data.meshes.new("Luminous dancer source body")
        v=np.asarray(data["model_vertices"])@np.asarray(B).T
        mesh.from_pydata(v.tolist(),[],data["model_triangles"].tolist());mesh.update()
        obj=bpy.data.objects.new("Editable dancer body",mesh)
        bpy.context.collection.objects.link(obj)
        groups=[obj.vertex_groups.new(name=n) for n in names]
        for vid,(indices,weights) in enumerate(zip(data["weight_indices"],data["weight_values"])):
            for bid,w in zip(indices,weights):
                if w>0:groups[int(bid)].add([vid],float(w),"ADD")
        mod=obj.modifiers.new("Native skin weights","ARMATURE");mod.object=arm
        mod.use_deform_preserve_volume=False
        material=bpy.data.materials.new("Warm luminous authoring preview")
        material.diffuse_color=(.68,.40,.16,1)
        obj.data.materials.append(material)
        for poly in obj.data.polygons:poly.use_smooth=True
    arm["authoring_source"]="Original native whole-body controls and IK"
    arm["capture"]="No motion capture extraction"
    arm["mapping"]="Modelled rest matrices and explicit native neutral corrections"
    return arm,names,parents


def validate_saved_armature(arm, data, meta):
    """Check the saved rest skeleton against the exact source rig definition."""
    if arm is None or arm.type != "ARMATURE":
        raise ValueError("Saved blend must contain the armature 'Fluid Fan Performance'")
    names=[str(s) for s in data["bone_names"]]
    parents=data["parents"]
    if set(arm.data.bones.keys()) != set(names) or len(arm.data.bones) != len(names):
        raise ValueError("Saved armature bone names differ from the source rig")
    for i,name in enumerate(names):
        parent=arm.data.bones[name].parent
        expected=None if parents[i] < 0 else names[parents[i]]
        if (parent.name if parent else None) != expected:
            raise ValueError("Saved armature hierarchy differs at " + name)
        if not arm.data.bones[name].use_deform:
            raise ValueError("A source deform bone was disabled: " + name)
    # Reconstruct only a temporary rest skeleton: never replace the saved action.
    reference,_,_=create_rest_armature(data,"__fluid_rest_validation__")
    matrix_error=tail_error=0.
    try:
        for name in names:
            actual=arm.data.bones[name];expected=reference.data.bones[name]
            matrix_error=max(matrix_error,float(np.max(np.abs(
                np.asarray(actual.matrix_local)-np.asarray(expected.matrix_local)))))
            tail_error=max(tail_error,(actual.tail_local-expected.tail_local).length)
    finally:
        reference_data=reference.data
        bpy.data.objects.remove(reference,do_unlink=True)
        bpy.data.armatures.remove(reference_data)
        bpy.context.view_layer.objects.active=arm
        arm.select_set(True)
    if matrix_error > 2e-6 or tail_error > 2e-6:
        raise ValueError(f"Saved rest pose changed: matrix={matrix_error}, tail={tail_error} m")
    scene=bpy.context.scene
    fps=meta["output_rate"][0]/meta["output_rate"][1]
    if abs(scene.render.fps/scene.render.fps_base-fps)>1e-8:
        raise ValueError("Saved scene frame rate differs from the source timing contract")
    if abs(scene.unit_settings.scale_length-1.)>1e-8:
        raise ValueError("Saved scene must retain metre scale (scale_length=1)")
    last_frame=1.+float(data["times"][-1])*fps
    if scene.frame_start>1 or scene.frame_end+1e-6<last_frame:
        raise ValueError("Saved scene does not cover source frame 1 through the final sample")
    if bpy.data.libraries:
        raise ValueError("Make the saved rig and animation local before exporting; linked libraries are unsupported")
    return dict(maximum_rest_matrix_error=matrix_error,maximum_rest_tail_error_m=tail_error,
                hierarchy="matched source",frame_rate=fps,frame_origin=1)


def write_action(arm,data,names,parents,fps):
    action=bpy.data.actions.new("Fluid Fan 12s - editable evaluated performance")
    arm.animation_data_create();arm.animation_data.action=action
    n=len(data["times"]);nb=len(names)
    location=np.zeros((n,nb,3));rotation=np.zeros((n,nb,4))
    maximum_scale_error=maximum_child_location=0.
    correction=[Quaternion(q) for q in data["neutral_correction"]]
    rests=[arm.data.bones[name].matrix_local.copy() for name in names]
    rest_rot=[m.to_3x3() for m in rests]
    for frame in range(n):
        desired=[]
        for j,name in enumerate(names):
            # Native world-neutral rotation A becomes model-rest rotation D=A*C.
            D=Quaternion(data["world_rotations"][frame,j])@correction[j]
            m=(B@D.to_matrix()@BI@rest_rot[j]).to_4x4()
            m.translation=B@Vector(data["positions"][frame,j])
            desired.append(m)
            bone=arm.data.bones[name]
            kwargs={}
            if parents[j]>=0:
                kwargs=dict(parent_matrix=desired[parents[j]],parent_matrix_local=rests[parents[j]])
            basis=bone.convert_local_to_pose(m,rests[j],invert=True,**kwargs)
            loc,q,scale=basis.decompose()
            location[frame,j]=loc;rotation[frame,j]=q
            maximum_scale_error=max(maximum_scale_error,max(abs(s-1) for s in scale))
            if parents[j]>=0:maximum_child_location=max(maximum_child_location,loc.length)
    rotation=continuity(rotation)
    frames=data["times"]*fps+1.
    for j,name in enumerate(names):
        path=arm.pose.bones[name].path_from_id()
        for prop,channels in (("location",location[:,j]),("rotation_quaternion",rotation[:,j])):
            for axis in range(channels.shape[-1]):
                fc=action.fcurves.new(path+"."+prop,index=axis,action_group=name)
                fc.keyframe_points.add(n)
                co=np.stack((frames,channels[:,axis]),axis=1).ravel()
                fc.keyframe_points.foreach_set("co",co)
                for k in fc.keyframe_points:k.interpolation="LINEAR"
                fc.update()
    if maximum_scale_error>1e-4 or maximum_child_location>2e-5:
        raise ValueError(f"Unsupported skeletal stretching: scale={maximum_scale_error}, child translation={maximum_child_location}")
    return dict(maximum_scale_error=maximum_scale_error,maximum_nonroot_translation_m=maximum_child_location)


def evaluate(arm,data,names,parents,fps):
    scene=bpy.context.scene
    rest_rot=[arm.data.bones[name].matrix_local.to_3x3() for name in names]
    correction=[Quaternion(q) for q in data["neutral_correction"]]
    samples=len(data["times"]);nb=len(names)
    local=np.zeros((samples,nb,4));root_q=np.zeros((samples,4));root_p=np.zeros((samples,3))
    evaluated_positions=np.zeros((samples,nb,3));evaluated_rotations=np.zeros((samples,nb,4))
    maximum_rigidity_error=maximum_translation_error=0.
    root_index=int(np.where(parents<0)[0][0])
    if root_index!=0 or int(np.sum(parents<0))!=1:raise ValueError("Exactly one first root is required")
    for idx,t in enumerate(data["times"]):
        ff=float(t)*fps+1
        scene.frame_set(int(np.floor(ff)),subframe=ff-np.floor(ff))
        arm_eval=arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
        qs=[]
        for j,name in enumerate(names):
            # Object-level rigid travel is included once in the stage-space root.
            m=arm_eval.matrix_world@arm_eval.pose.bones[name].matrix
            numeric=np.asarray(m,dtype=np.float64)
            if not np.isfinite(numeric).all():
                raise ValueError(f"Nonfinite evaluated bone {name} at t={t}")
            rotation=numeric[:3,:3]
            rigidity=float(np.max(np.abs(rotation.T@rotation-np.eye(3))))
            maximum_rigidity_error=max(maximum_rigidity_error,rigidity)
            if rigidity>1e-4 or np.linalg.det(rotation)<=0:
                raise ValueError(f"Unsupported evaluated scale, shear or reflection: {name} at t={t}")
            D=(BI@m.to_3x3()@rest_rot[j].transposed()@B).to_quaternion().normalized()
            A=(D@correction[j].conjugated()).normalized()
            P=BI@m.translation
            qs.append(A)
            evaluated_positions[idx,j]=P;evaluated_rotations[idx,j]=A
            if parents[j]<0:
                root_p[idx]=P;root_q[idx]=A;local[idx,j]=(1,0,0,0)
            else:
                local[idx,j]=(qs[parents[j]].conjugated()@A).normalized()
                offset=Vector(data["neutral_positions"][j]-data["neutral_positions"][parents[j]])
                expected=Vector(evaluated_positions[idx,parents[j]])+qs[parents[j]]@offset
                error=(P-expected).length
                maximum_translation_error=max(maximum_translation_error,error)
                if error>2e-5:
                    raise ValueError(f"Unsupported bone translation/stretch: {name} at t={t}, error={error} m")
    local=continuity(local);root_q=continuity(root_q);evaluated_rotations=continuity(evaluated_rotations)
    return dict(local_rotations=local.astype(np.float32),root_rotations=root_q.astype(np.float32),
        root_positions=root_p.astype(np.float32),evaluated_positions=evaluated_positions,
        evaluated_world_rotations=evaluated_rotations,
        evaluation_validation=dict(maximum_evaluated_rigidity_error=maximum_rigidity_error,
            maximum_native_joint_reconstruction_error_m=maximum_translation_error))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,help="Original authoring-input.npz for rig and timing")
    p.add_argument("--output",required=True,help="Destination performance.npz")
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--blend",help="Build and save a new editable armature from authored input")
    mode.add_argument("--from-blend",help="Evaluate this saved armature without changing its keys or saving it")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    src=Path(a.input).resolve();out=Path(a.output).resolve()
    blend=Path(a.from_blend or a.blend).resolve()
    existing=bool(a.from_blend)
    reference_path=out.with_name(out.stem+"-evaluated.npz")
    if out.suffix!=".npz" or out==src or out==blend:
        p.error("Use a distinct .npz output path")
    if existing and any(path.exists() for path in (out,out.with_suffix(".json"),reference_path)):
        p.error("Saved-blend export requires a new output path; retain previous bundles for review")
    meta=json.loads(src.with_suffix(".json").read_text())
    if meta["source_npz_sha256"]!=sha(src):raise ValueError("Authored input checksum mismatch")
    with np.load(src,allow_pickle=False) as d:data={k:d[k] for k in d.files}
    fps=meta["output_rate"][0]/meta["output_rate"][1]
    source_blend_hash=None
    if existing:
        source_blend_hash=sha(blend)
        bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
        arm=bpy.data.objects.get("Fluid Fan Performance")
        action_validation=validate_saved_armature(arm,data,meta)
        names=[str(s) for s in data["bone_names"]];parents=data["parents"]
    else:
        arm,names,parents=build_armature(data)
        scene=bpy.context.scene;scene.render.fps=int(fps);scene.frame_start=1
        scene.frame_end=int(round(float(data["times"][-1])*fps))+1
        scene.unit_settings.system="METRIC";scene.unit_settings.scale_length=1.
        action_validation=write_action(arm,data,names,parents,fps)
    result=evaluate(arm,data,names,parents,fps)
    receipt=dict(blender_version=bpy.app.version_string,samples=len(data["times"]),bone_count=len(names),
        **action_validation,**result["evaluation_validation"])
    if existing:
        receipt["comparison_to_original_authored_motion"]="not asserted: saved animation may be edited"
    else:
        position_error=float(np.linalg.norm(result["evaluated_positions"]-data["positions"],axis=-1).max())
        qa=result["evaluated_world_rotations"];qb=data["world_rotations"]
        dot=np.abs(np.sum(qa*qb,axis=-1));angle_error=float((2*np.arccos(np.clip(dot,0,1))).max())
        receipt.update(maximum_joint_roundtrip_error_m=position_error,
            maximum_rotation_roundtrip_error_radians=angle_error)
        if position_error>2e-5 or angle_error>.001:raise ValueError(f"Blender rig roundtrip failed: {receipt}")
    out.parent.mkdir(parents=True,exist_ok=True)
    contact=np.zeros_like(data["contact"]) if existing else data["contact"]
    labels=(np.full((len(data["times"]),2),"unknown",dtype="U24") if existing else
            data.get("support_labels",np.full((len(data["times"]),2),"unknown",dtype="U24")))
    np.savez_compressed(out,times=data["times"],local_rotations=result["local_rotations"],
        root_rotations=result["root_rotations"],root_positions=result["root_positions"],
        neutral_positions=data["neutral_positions"],neutral_correction=data["neutral_correction"],
        contact=contact,support_labels=labels,
        fan_openings=data.get("fan_openings",np.ones((len(data["times"]),2),dtype=np.float32)),
        local_translations=np.asarray([
            np.zeros(3) if p<0 else data["neutral_positions"][i]-data["neutral_positions"][p]
            for i,p in enumerate(parents)]))
    if existing:
        if sha(blend)!=source_blend_hash:
            raise RuntimeError("Source Blender file changed during export")
        # Validate the native adapter against this saved animation, not old poses.
        np.savez_compressed(reference_path,times=data["times"],
            positions=result["evaluated_positions"],world_rotations=result["evaluated_world_rotations"])
    else:
        blend.parent.mkdir(parents=True,exist_ok=True)
        bpy.context.scene.frame_set(1)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    manifest=dict(schema=SCHEMA,description="Blender-evaluated bake of original authored whole-body fan choreography.",
        authoring="Saved Blender armature animation, based on native authored input" if existing else meta["authoring"],
        export_mode="saved_blend" if existing else "authored_input",capture=False,rig=meta["rig"],sample_rate=meta["sample_rate"],
        output_rate=meta["output_rate"],duration_seconds=meta["duration_seconds"],samples=meta["samples"],
        coordinates=dict(handedness="right",units="metres",up="+Y",forward="+Z",anatomical_left="+X",
            native_to_blender_basis=[list(row) for row in B],quaternion="Hamilton wxyz active",root="absolute stage transform",
            local_rotations="parent-relative neutral-frame rotations; modeled-rest correction C applied once by native Rig.fk",
            local_translations="constant parent-relative neutral offsets; root offset stored separately",matrix_convention="column vectors"),
        interpolation="linear root translation and shortest-path local/root quaternion slerp; hold endpoints",loop=False,
        npz_sha256=sha(out),authoring_input_sha256=sha(src),authoring_blend_sha256=sha(blend),
        source_commit=meta["source_commit"],authored_score_sha256=meta["authored_score_sha256"],
        source_files=meta.get("source_files",{}),
        support_annotation_origin="unresolved after saved Blender export" if existing else meta.get("support_annotation_origin","unknown"),
        support_labels=["unknown"] if existing else meta.get("support_labels",["unknown"]),
        authoring_times=[] if existing else meta.get("authoring_times",[]),
        exporter_sha256=sha(Path(__file__)),blender_validation=receipt,
        review_status="numeric bridge verified; artistic review required",
        scope="Editable deforming armature and evaluated export. No external mocap, new toe bones, new control-rig UI, or Blender cloth export.")
    if existing:
        manifest.update(description="Evaluated export from a saved Blender armature; original pose equality is not assumed.",
            saved_blend_source=dict(filename=blend.name,sha256=source_blend_hash,
                embedded_scripts_enabled=False,source_file_modified=False),
            original_authoring=meta["authoring"],
            evaluated_reference=dict(filename=reference_path.name,sha256=sha(reference_path),
                comparison_target="current saved Blender evaluation"),
            original_support_annotation_origin=meta.get("support_annotation_origin","unknown"),
            support_annotations_status="all unknown; contact=false means no asserted support, not verified airborne",
            fan_openings_origin="unchanged source channels; review alongside edited poses",
            timing_mapping="source timestamp t maps to Blender frame 1 + t * output_rate; source duration retained",
            review_status="rig and evaluated transform compatibility verified; contacts and artistic review required")
    out.with_suffix(".json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("FLUID_BLEND_BAKE "+json.dumps(receipt))


if __name__=="__main__":main()
