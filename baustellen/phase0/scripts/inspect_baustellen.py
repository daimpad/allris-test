import json,sys,glob,collections
for f in sorted(glob.glob(sys.argv[1]+'/thema_*.geojson')):
    d=json.load(open(f,encoding='utf-8'))
    fs=d['features']
    print('==',f.split('/')[-1],'n=',len(fs),'top keys',list(d.keys()))
    print(' geom',collections.Counter(x['geometry']['type'] if x.get('geometry') else None for x in fs))
    keys=collections.Counter(k for x in fs for k in x['properties'])
    print(' props',dict(keys))
    ids=[x['properties'].get('baustelle_id') for x in fs]; print(' ids unique',len(set(ids)),'min/max',min(ids),max(ids))
    for k in keys:
        vals=collections.Counter(str(x['properties'].get(k)) for x in fs)
        if len(vals)<=15: print('  ',k,dict(vals.most_common(15)))
        else: print('  ',k,'distinct',len(vals),'e.g.',list(vals)[:4])
    for x in fs[:3]: print(' BSP',json.dumps(x,ensure_ascii=False)[:700])
