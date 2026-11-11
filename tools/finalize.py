# Final master: concat the per-scene ProRes renders from Resolve, encode H.264 + AAC with the timeline mix, verify.
# usage (from vaultx/): python -I tools/finalize.py [--deliver | --deliver-only]
#   --deliver       encode, then rebuild ~/Downloads/Task5 with only the brief's deliverables
#   --deliver-only  skip the encode (master already built), just rebuild Task5
# Scene renders are read from ~/vxs/chunks (VX_C01.mov ... or a/b/c pieces), the Resolve archive from ~/vxs/archive.
import os
import shutil
import subprocess
import sys

CH = os.path.expanduser(os.path.join('~', 'vxs', 'chunks'))
ARC = os.path.expanduser(os.path.join('~', 'vxs', 'archive'))
OUT = os.path.abspath('deliverables')
MASTER = os.path.join(OUT, 'VaultX_Wallet_Ad_1920x1080_H264.mp4')
TASK = os.path.expanduser(os.path.join('~', 'Downloads', 'Task5'))
os.makedirs(OUT, exist_ok=True)


def nframes(path):
    q = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True)
    return int([l for l in q.stderr.replace('\r', '\n').splitlines() if 'frame=' in l][-1].split('frame=')[1].split()[0])


EXPECT = [105, 162, 114, 126, 99, 141, 201, 198, 204]
chunks = []
for i in range(1, 10):
    whole = os.path.join(CH, 'VX_C%02d.mov' % i)
    parts = [os.path.join(CH, 'VX_C%02d%s.mov' % (i, s)) for s in 'abc' if os.path.exists(os.path.join(CH, 'VX_C%02d%s.mov' % (i, s)))]
    use = parts if parts else [whole]
    n = sum(nframes(c) for c in use)
    assert n == EXPECT[i - 1], ('scene C%02d has %d frames, expected %d' % (i, n, EXPECT[i - 1]))
    chunks += use
print('chunks ok:', [os.path.basename(c) for c in chunks])

if '--deliver-only' not in sys.argv:
    lst = os.path.join(OUT, '_concat.txt')
    open(lst, 'w').write(''.join("file '%s'\n" % c.replace('\\', '/') for c in chunks))
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', 'build/audio/MIX_reference.wav',
           '-map', '0:v:0', '-map', '1:a:0', '-map_metadata', '-1', '-c:v', 'libx264', '-preset', 'slow',
           '-b:v', '16M', '-maxrate', '24M', '-bufsize', '32M', '-tune', 'animation',
           '-profile:v', 'high', '-level', '4.1', '-pix_fmt', 'yuv420p', '-r', '30', '-g', '60', '-write_tmcd', '0',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv',
           '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-t', '45', '-movflags', '+faststart', MASTER]
    subprocess.run(cmd, check=True)
    os.remove(lst)

# verify: frame count, streams, loudness
info = subprocess.run(['ffmpeg', '-hide_banner', '-i', MASTER], capture_output=True, text=True).stderr
streams = [l.strip() for l in info.splitlines() if 'Stream #' in l]
q = subprocess.run(['ffmpeg', '-hide_banner', '-i', MASTER, '-map', '0:a', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
I = q.split('I:')[-1].split('LUFS')[0].strip()
tp = q.split('Peak:')[-1].split('dBFS')[0].strip()
print('master', os.path.getsize(MASTER) // 1024, 'KB |', nframes(MASTER), 'frames | I', I, 'LUFS | TP', tp)
for s in streams:
    print('  ', s[:140])

if '--deliver' in sys.argv or '--deliver-only' in sys.argv:
    # Task5 holds only what the brief asks for: final video, collected project, custom assets (+ README for the music credit)
    if os.path.exists(TASK):
        for f in os.listdir(TASK):
            p = os.path.join(TASK, f)
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    os.makedirs(TASK, exist_ok=True)
    shutil.copy2(MASTER, TASK)
    shutil.copy2(os.path.join(OUT, 'README.md'), TASK)
    shutil.copytree(os.path.join(OUT, 'assets'), os.path.join(TASK, 'Assets'))
    pj = os.path.join(TASK, 'Project')
    os.makedirs(pj)
    shutil.copytree('assets/fonts', os.path.join(pj, 'Fonts'))
    shutil.make_archive(os.path.join(pj, 'VaultX_Wallet_Ad_Resolve_Archive'), 'zip', ARC, 'VaultX_Wallet_Ad.dra')
    print('delivered to', TASK)
