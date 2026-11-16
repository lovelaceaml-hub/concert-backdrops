"""Exact campaign words, quietly legible over the cinematic environments."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path(__file__).resolve().parents[2]

class Phrases:
    def __init__(self,w,h,film):
        self.w=w;self.h=h;self.film=film;self.layers=[];s=h/1080
        self.label=Image.new('RGBA',(w,h));ld=ImageDraw.Draw(self.label)
        lf=ImageFont.truetype(str(ROOT/'fonts/outfit-latin-500-normal.ttf'),round(17*s))
        ld.text((.96*w,.965*h),'GPT-6.1 SOL',font=lf,anchor='rs',fill='#fff4de',stroke_width=0)
        self.day_label=Image.new('RGBA',(w,h));dd=ImageDraw.Draw(self.day_label)
        dd.text((.96*w,.965*h),'GPT-6.1 SOL',font=lf,anchor='rs',fill='#272751')
        font=ImageFont.truetype(str(ROOT/'fonts/cormorant-garamond-latin-600-italic.ttf'),round(68*s))
        for spec,expression in zip(film._SPECS,film.PW.EXPRESSIONS):
            layer=Image.new('RGBA',(w,h));d=ImageDraw.Draw(layer)
            lines=[]
            for raw in expression['lines']:
                line=''
                for word in raw.split():
                    trial=(line+' '+word).strip()
                    if font.getlength(trial)>670*s and line:lines.append(line);line=word
                    else:line=trial
                if line:lines.append(line)
            reflow={
                'Gratitude':['“Thank you.','It’s all thanks to you.','You’ve worked hard.”'],
                'Apology':['“I’m sorry.','It must have been','hard on you.”'],
                'Inclusiveness':['“It’s okay.','I understand.”']}
            if expression['label'] in reflow:
                lines=reflow[expression['label']]
                assert ' '.join(lines)==' '.join(expression['lines'])
            x,y=round(.095*w),round(.27*h)
            ink='#272751' if expression['label'] in ('Gratitude','Apology','Inclusiveness','Encouragement') else '#fff4de'
            for k,line in enumerate(lines):
                d.text((x,y+k*77*s),line,font=font,fill=ink,stroke_width=0)
            yy=y+len(lines)*77*s+12*s
            d.line((x,yy,x+80*s,yy),fill=expression['color'],width=max(1,round(3*s)))
            # A soft cream halo follows the letters, leaving the scenery visible.
            mask=layer.getchannel('A').filter(ImageFilter.GaussianBlur(6*s))
            glow=Image.new('RGBA',(w,h),'#f4c887');glow.putalpha(mask.point(lambda q:round(q*.7)))
            glow.alpha_composite(layer)
            self.layers.append((spec,glow))
    def apply(self,image,t):
        image=image.convert('RGBA');image.alpha_composite(self.day_label if t>54 else self.label)
        for spec,layer in self.layers:
            a,b=spec['t_in'],spec['t_out']
            if not a<=t<=b:continue
            g=self.film.film.sc(a,spec['t_read0'],t)*(1-self.film.film.sc(spec['t_read1'],b,t))
            if g<=0:return image.convert('RGB')
            if image.mode!='RGBA':image=image.convert('RGBA')
            if g<.999:
                layer=layer.copy();layer.putalpha(layer.getchannel('A').point(lambda q:round(q*g)))
            image.alpha_composite(layer)
            return image.convert('RGB')
        return image.convert('RGB')


def smaller_signature():
    import titles
    original=titles.Titles._signature
    def signature(self,corner,palette):
        old=self.s;self.s*=.60
        try:return original(self,corner,palette)
        finally:self.s=old
    titles.Titles._signature=signature
