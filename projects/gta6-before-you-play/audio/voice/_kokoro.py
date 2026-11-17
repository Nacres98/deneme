
import sys, json, numpy as np, soundfile as sf, warnings
warnings.filterwarnings('ignore')
from kokoro import KPipeline
job = json.load(open(sys.argv[1]))
p = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
for item in job['lines']:
    parts = [a for _, _, a in p(item['text'], voice=job['voice'], speed=job['speed'])]
    aud = np.concatenate(parts) if parts else np.zeros(2400, np.float32)
    sf.write(item['out'], aud, 24000)
    print(item['out'], round(len(aud) / 24000, 2), flush=True)
