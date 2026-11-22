import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';

const root=path.dirname(fileURLToPath(import.meta.url));
const output=await bundle({entryPoint:path.join(root,'src/index.ts'),publicDir:path.join(root,'public'),outDir:path.join(root,'dist')});
console.log(`Remotion bundle: ${output}`);
