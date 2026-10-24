"""Run: docker compose exec backend python sync_catalog.py --languages en ja"""
import argparse
import asyncio
import httpx
from app.catalog import connect, count

BASE='https://api.tcgdex.net/v2'

async def sync_language(client, lang):
    sets = (await fetch(client, f'{BASE}/{lang}/sets'))
    index = {s['id']:s for s in sets if isinstance(s,dict) and s.get('id')}
    total=0
    for page in range(1,1000):
        cards=await fetch(client,f'{BASE}/{lang}/cards',params={'pagination:page':page,'pagination:itemsPerPage':250})
        if not isinstance(cards,list):
            raise RuntimeError(f'Unexpected card list for {lang}')
        entries=[]
        for c in cards:
            cid=c.get('id',''); local=str(c.get('localId',''))
            if not cid or not local or not c.get('name'):
                continue
            sid=cid.rsplit('-',1)[0]
            st=index.get(sid,{})
            card_count=st.get('cardCount') or {}
            denom=card_count.get('total') if isinstance(card_count,dict) else None
            number=f'{local}/{denom}' if denom else local
            img=c.get('image') or ''
            entries.append((f'{lang}:{cid}',lang,c['name'],local,number,sid,st.get('name',''),img))
        with connect() as db:
            db.executemany('INSERT OR REPLACE INTO cards VALUES (?,?,?,?,?,?,?,?)',entries)
            db.commit()
        total+=len(entries)
        print(f'{lang}: indexed {total} cards',flush=True)
        if len(cards)<250:
            break
    return total

async def fetch(client,url,params=None):
    for attempt in range(4):
        try:
            r=await client.get(url,params=params)
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPError,ValueError):
            if attempt==3:
                raise
            await asyncio.sleep(2**attempt)

async def main():
    p=argparse.ArgumentParser()
    p.add_argument('--languages',nargs='+',default=['en','ja'])
    args=p.parse_args()
    async with httpx.AsyncClient(timeout=40,headers={'User-Agent':'DeckFlow-CPSC490/1.0'}) as client:
        for lang in args.languages:
            n=await sync_language(client,lang)
            print(f'Synced {lang}: {n} entries',flush=True)
    print('Catalog ready, total rows:',count())

if __name__=='__main__':
    asyncio.run(main())
