# Lua batches for the Resolve Console: import VO / music / SFX clips into labelled bins and lay them on named
# audio tracks of VaultX_Ad_Master (A1 VO, A2 Music, A3+ SFX). Clip gains are baked into the wavs, faders stay 0 dB,
# so the timeline sums to build/audio/MIX_reference.wav.
# usage (from vaultx/): python -I tools/make_resolve_audio.py -> build/resolve_audio.txt (one Lua line per batch)
import json
import os

ROOT = os.path.abspath('.').replace('\\', '\\\\')
AUD = ROOT + '\\\\build\\\\audio\\\\'
cues = json.load(open('build/audio/sfx_cues.json'))['clips']
# greedy SFX track assignment (no overlaps on a track)
tracks = []
for c in sorted(cues, key=lambda c: c['frame']):
    for ti, end in enumerate(tracks):
        if c['frame'] >= end + 1:
            tracks[ti] = c['frame'] + c['frames']
            c['track'] = ti
            break
    else:
        tracks.append(c['frame'] + c['frames'])
        c['track'] = len(tracks) - 1
ns = len(tracks)
Q = chr(34)
L = []
L.append('mp=p:GetMediaPool();ms=resolve:GetMediaStorage();root=mp:GetRootFolder();'
         'function D(t) local o={};for k,v in pairs(t) do if type(v)=="userdata" then o[#o+1]=v end end;return o end;'
         'function SUB(par,n) for _,f in ipairs(D(par:GetSubFolderList())) do if f:GetName()==n then return f end end;return mp:AddSubFolder(par,n) end;'
         'BA=SUB(root,"02_Audio");BV=SUB(BA,"VO");BM=SUB(BA,"Music");BS=SUB(BA,"SFX");'
         f'mp:SetCurrentFolder(BV);ms:AddItemListToMediaPool({{"{AUD}A1_VO_VaultX.wav"}});'
         f'mp:SetCurrentFolder(BM);ms:AddItemListToMediaPool({{"{AUD}A2_Music_ZoneX_InnovationNeeded_edit.wav"}});'
         'mp:SetCurrentFolder(BS);'
         + f'ms:AddItemListToMediaPool({{{",".join(Q + AUD + "sfx_clips\\\\" + c["file"] + Q for c in cues)}}});'
         'c={};for _,b in ipairs({BV,BM,BS}) do for _,v in ipairs(D(b:GetClipList())) do c[v:GetName()]=v end end;'
         'n=0;for _ in pairs(c) do n=n+1 end;print("pool audio",n)')
L.append('base=tl:GetStartFrame();while tl:GetTrackCount("audio")<%d do tl:AddTrack("audio","stereo") end;' % (2 + ns)
         + 'tl:SetTrackName("video",1,"Scenes - Fusion comps C01-C09");tl:SetTrackName("audio",1,"VO");'
         'tl:SetTrackName("audio",2,"Music - ZoneX Innovation Needed (CC BY 3.0)");'
         + ';'.join('tl:SetTrackName("audio",%d,"SFX %d")' % (i + 3, i + 1) for i in range(ns))
         + ';FAILS=0;function A(n,k,t,f) local it=c[n]; if not it then FAILS=FAILS+1;print("MISSING",n);return end;'
         'local q=mp:AppendToTimeline({{mediaPoolItem=it,startFrame=0,endFrame=k,trackIndex=t,recordFrame=base+f,mediaType=2}});'
         'if not q or #q==0 then FAILS=FAILS+1;print("FAIL",n) end end;'
         'A("A1_VO_VaultX.wav",1350,1,0);A("A2_Music_ZoneX_InnovationNeeded_edit.wav",1350,2,0);print("vo/music",FAILS)')
rows = ['A("%s",%d,%d,%d)' % (c['file'], c['frames'], c['track'] + 3, c['frame']) for c in cues]
L.append(';'.join(rows) + ';print("sfx placed",%d,"fails",FAILS)' % len(cues))
L.append('s="";for i=1,tl:GetTrackCount("audio") do s=s.." A"..i.."="..#D(tl:GetItemListInTrack("audio",i)) end;print(s);'
         'print("save",resolve:GetProjectManager():SaveProject())')
open('build/resolve_audio.txt', 'w', encoding='utf8').write('\n'.join(L))
print(len(L), 'batches', [len(x) for x in L], 'sfx tracks', ns)
