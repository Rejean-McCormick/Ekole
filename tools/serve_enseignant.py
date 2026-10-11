#!/usr/bin/env python3
"""Ekole Enseignant local preview, isolated from site/ and non-public.
Not a production school authentication system. No remote binding.
"""
from __future__ import annotations
import argparse, http.server, json, pathlib, re, secrets, webbrowser, mimetypes, io, os, shutil, tempfile, hashlib
from urllib.parse import urlsplit, parse_qs
ROOT=pathlib.Path(__file__).resolve().parents[1]
VALID_COURSE=re.compile(r'^qc-pri-[a-z]+-\d{3}$')

def create_handler(root,token):
    root=pathlib.Path(root).resolve()
    csrf_token=secrets.token_urlsafe(36)
    class Handler(http.server.BaseHTTPRequestHandler):
        def respond(self,code,content=b'',typ='text/plain; charset=utf-8',headers=()):
            self.send_response(code)
            self.send_header('Content-Type',typ)
            self.send_header('Content-Length',str(len(content)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Permissions-Policy','camera=(), microphone=(), geolocation=()')
            self.send_header('Content-Security-Policy',"default-src 'self'; connect-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data: blob:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
            for k,v in headers:self.send_header(k,v)
            self.end_headers();self.wfile.write(content)
        def do_GET(self):
            path=urlsplit(self.path);route=path.path
            if route=='/open':
                candidate=parse_qs(path.query).get('key',[''])[0]
                if secrets.compare_digest(candidate,token):
                    self.send_response(303)
                    self.send_header('Location','/')
                    self.send_header('Set-Cookie',f'EkoleTeacher={token}; HttpOnly; SameSite=Strict; Path=/')
                    self.send_header('Cache-Control','no-store')
                    self.send_header('Referrer-Policy','no-referrer')
                    self.end_headers();return
                return self.respond(403,b'Acces refuse')
            cookies=self.headers.get('Cookie','')
            # Session cookie required for every static and API endpoint.
            actual={s.strip().split('=',1)[1] for s in cookies.split(';') if s.strip().startswith('EkoleTeacher=') and '=' in s}
            if not any(secrets.compare_digest(x,token) for x in actual):
                return self.respond(401,b'Ekole Enseignant: lancer tools/serve_enseignant.py --open et utiliser le navigateur ouvert.')
            if route in ('/','/index.html','/app.js','/style.css','/planification-v8.js','/images-editor-v15.js'):
                sub='index.html' if route in ('/','/index.html') else route[1:]
                f=root/'enseignant-app'/sub
            elif route=='/api/index.json':
                public=json.loads((root/'site/data/index.json').read_text(encoding='utf-8'))
                student=json.loads((root/'site/eleve/data/eleves/catalogue.json').read_text(encoding='utf-8'))
                year_by_id={c['id']:c for c in student.get('courses',[])}
                for c in public.get('courses',[]):
                    p=year_by_id.get(c['id'],{})
                    c['year_suggestion']=p.get('year_suggestion')
                    c['step_suggestion']=p.get('step_suggestion')
                return self.respond(200,(json.dumps(public,ensure_ascii=False)+'\n').encode('utf-8'),'application/json; charset=utf-8')
            elif route in ('/atelier-v12/','/atelier-v12/index.html','/atelier-v12/app.js','/atelier-v12/style.css'):
                sub='index.html' if route in ('/atelier-v12/','/atelier-v12/index.html') else route.rsplit('/',1)[1]
                f=root/'enseignant-app/atelier-v12'/sub
            elif route=='/api/plan-v12.json':f=root/'docs/PLAN_TRANSFORMATION_202_V12.json'
            elif route=='/api/couverture-v14.json':f=root/'docs/AUDIT_ACTIVITES_202_V14.json'
            elif route.startswith('/api/cadre-v12/') and route.endswith('.json'):
                id=route[len('/api/cadre-v12/'):-5]
                if not VALID_COURSE.fullmatch(id):return self.respond(404,b'Not found')
                f=root/'kristals'/id/'experience/CADRE_PEDAGOGIQUE_V12.json'
                if f.is_symlink():return self.respond(404,b'Not found')
            elif route=='/api/labo-catalogue.json':f=root/'site/eleve/labo/data/catalogue.json'
            elif route=='/api/visuals.json':f=root/'visuels/INTENTIONS_IMAGES.json'
            elif route=='/api/kristal-visuals.json':f=root/'site/eleve/data/kristals-visuels.json'
            elif route in ('/cadres-images/','/cadres-images/index.html','/cadres-images/app.js','/cadres-images/style.css'):
                sub='index.html' if route in ('/cadres-images/','/cadres-images/index.html') else route.rsplit('/',1)[1]
                f=root/'enseignant-app/cadres-images'/sub
            elif route=='/cadres-images/frame-styles.css':
                f=root/'site/eleve/cadres-images.css'
            elif route in ('/images-album/','/images-album/index.html','/images-album/app.js','/images-album/style.css'):
                sub='index.html' if route in ('/images-album/','/images-album/index.html') else route.rsplit('/',1)[1]
                f=root/'enseignant-app/images-album'/sub
            elif route=='/images-album/frame-styles.css':
                f=root/'site/eleve/cadres-images.css'
            elif route=='/api/images-album.json':
                from inventaire_images_v21 import inventory
                result=inventory(root)
                return self.respond(200,(json.dumps(result,ensure_ascii=False)+'\n').encode('utf-8'),'application/json; charset=utf-8')
            elif route=='/api/cadres-images.json':
                f=root/'site/eleve/data/cadres-images.json'
            elif route=='/api/image-editor-config.json':
                return self.respond(200,(json.dumps({'csrf':csrf_token,'max_upload_bytes':12*1024*1024,'formats':['webp','png','jpeg'],'max_widths':[768,1024,1536,2048]})+'\n').encode('utf-8'),'application/json; charset=utf-8')
            elif route.startswith('/api/experience/') and route.endswith('.json'):
                id=route[len('/api/experience/'):-5]
                if not VALID_COURSE.fullmatch(id):return self.respond(404,b'Not found')
                f=root/'kristals'/id/'experience/SCENARIO_APPRENTISSAGE.json'
                if f.is_symlink():return self.respond(404,b'Not found')
            elif route.startswith('/api/kristal-image/'):
                tail=route[len('/api/kristal-image/'):]
                m=re.fullmatch(r'(qc-pri-[a-z]+-[0-9]{3})/([a-z][a-z0-9_-]{1,48}\.(?:webp|png|jpg|jpeg))',tail)
                if not m:return self.respond(404,b'Not found')
                f=root/'site/eleve/assets/kristals'/m[1]/m[2]
                if f.is_symlink() or not f.resolve().is_relative_to((root/'site/eleve/assets/kristals').resolve()):
                    return self.respond(404,b'Not found')
            elif route.startswith('/api/course/') and route.endswith('.json'):
                id=route[len('/api/course/'):-5]
                if not VALID_COURSE.fullmatch(id):return self.respond(404,b'Not found')
                f=root/'site/data/cours'/(id+'.json')
            else:return self.respond(404,b'Not found')
            if not f.is_file():return self.respond(404,b'Not found')
            m=mimetypes.guess_type(f.name)[0] or 'application/octet-stream'
            if f.suffix in ('.html','.css','.js','.json'):m+='; charset=utf-8'
            # no filesystem lookup from user-controlled paths except strict ID
            return self.respond(200,f.read_bytes(),m)
        def do_DELETE(self):
            """Teacher-only removal of ONE declared image slot, with a private backup.

            Never delete a file from a name supplied by the browser alone: require
            that (course, slot) exists in the canonical visual manifest.
            """
            route=urlsplit(self.path).path
            match=re.fullmatch(r'/api/visual-image/(qc-pri-[a-z]+-[0-9]{3})/([a-z][a-z0-9_-]{1,48})',route)
            if not match:return self.respond(404,b'Not found')
            cookies=self.headers.get('Cookie','')
            actual={c.strip().split('=',1)[1] for c in cookies.split(';') if c.strip().startswith('EkoleTeacher=') and '=' in c}
            if not any(secrets.compare_digest(x,token) for x in actual):return self.respond(401,b'Session Enseignant requise')
            expected_origin=f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Origin')!=expected_origin:return self.respond(403,b'Origine interdite')
            if not secrets.compare_digest(self.headers.get('X-Ekole-CSRF',''),csrf_token):return self.respond(403,b'Jeton de session invalide')
            if self.headers.get('X-Ekole-Delete-Confirm')!='yes':return self.respond(400,b'Confirmation de suppression requise')
            kid,slot=match.groups()
            workspace=root/'kristals'/kid
            manifest=workspace/'experience/RESSOURCES_VISUELLES.json'
            if workspace.is_symlink() or manifest.is_symlink() or not manifest.is_file() or not manifest.resolve().is_relative_to(workspace.resolve()):
                return self.respond(404,b'Kristal source non disponible')
            try:
                cfg=json.loads(manifest.read_text(encoding='utf-8'))
                if cfg.get('format')!='ekole.kristal-visual-layer/1.0' or cfg.get('kristal_id')!=kid or slot not in [x.get('slot') for x in cfg.get('visuels',[])]:
                    return self.respond(422,b'Emplacement inconnu dans le Kristal')
                image_dir=workspace/'experience/images'
                if image_dir.is_symlink() or not image_dir.resolve().is_relative_to(workspace.resolve()):
                    return self.respond(403,b'Chemin image refuse')
                existing=[image_dir/(slot+ext) for ext in ('.webp','.png','.jpg','.jpeg') if (image_dir/(slot+ext)).exists() or (image_dir/(slot+ext)).is_symlink()]
                if not existing:return self.respond(404,b'Aucune image a effacer pour cet emplacement')
                if any(p.is_symlink() or not p.is_file() for p in existing):return self.respond(403,b'Lien symbolique ou fichier inconnu refuse')
                originals={p:p.read_bytes() for p in existing}
                # Remove only public derivatives that are exact copies of the
                # canonical file. Never erase a customized public asset.
                public_dir=root/'site/eleve/assets/kristals'/kid
                if public_dir.is_symlink():return self.respond(403,b'Dossier public non autorise')
                public_copies={}
                for p,data in originals.items():
                    pub=public_dir/p.name
                    if pub.is_symlink():return self.respond(403,b'Lien symbolique public refuse')
                    if pub.is_file() and pub.read_bytes()==data:public_copies[pub]=data
                # Backups live outside site/eleve and are never exported to students.
                backup_dir=root/'archives'/'ekole-images'/kid
                for part in (root/'archives',root/'archives/ekole-images',backup_dir):
                    if part.is_symlink():return self.respond(403,b'Archive en lien symbolique interdite')
                backup_dir.mkdir(parents=True,exist_ok=True)
                backups=[]
                for p,data in originals.items():
                    backup=backup_dir/(p.name+'.suppression-'+secrets.token_hex(9)+'.bak')
                    with backup.open('xb') as out:out.write(data)
                    backups.append(backup.name)
                try:
                    for p in originals:p.unlink()
                    from compiler_visuels_kristals import compile_layer
                    published=compile_layer(root)
                    projected=next(x for x in published['cours'][kid]['visuels'] if x['slot']==slot)
                    if projected.get('url'):raise RuntimeError('La projection indique encore une image')
                    for p in public_copies:p.unlink()
                except Exception:
                    for p,data in originals.items():p.write_bytes(data)
                    for p,data in public_copies.items():
                        if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
                    from compiler_visuels_kristals import compile_layer
                    compile_layer(root)
                    raise
                res={'status':'deleted','kristal_id':kid,'slot':slot,'deleted_files':[p.name for p in existing],
                     'backup_files':backups,'public_url':None,'statut':'prompt_visible'}
                return self.respond(200,(json.dumps(res,ensure_ascii=False)+'\n').encode('utf-8'),'application/json; charset=utf-8')
            except (ValueError,OSError,RuntimeError,KeyError,StopIteration) as exc:
                return self.respond(422,('Suppression refusee : '+str(exc)).encode('utf-8'))
            except Exception:
                return self.respond(500,b'Erreur de suppression : consulter le journal local')
        def do_POST(self):
            """Validated loopback upload; never available on the public student host."""
            route=urlsplit(self.path).path
            if route=='/api/images-album/recompiler':
                cookies=self.headers.get('Cookie','')
                actual={c.strip().split('=',1)[1] for c in cookies.split(';') if c.strip().startswith('EkoleTeacher=') and '=' in c}
                if not any(secrets.compare_digest(x,token) for x in actual):return self.respond(401,b'Session Enseignant requise')
                if self.headers.get('Origin')!=f'http://127.0.0.1:{self.server.server_port}':return self.respond(403,b'Origine interdite')
                if not secrets.compare_digest(self.headers.get('X-Ekole-CSRF',''),csrf_token):return self.respond(403,b'Jeton invalide')
                try:
                    from compiler_visuels_kristals import compile_layer
                    result=compile_layer(root)
                    payload={'status':'synchronized','course_count':result['nb_cours_couverts'],'image_count':result['nb_images']}
                    return self.respond(200,(json.dumps(payload)+'\n').encode('utf-8'),'application/json; charset=utf-8')
                except (ValueError,OSError) as exc:
                    return self.respond(422,('Compilation refusee : '+str(exc)).encode('utf-8'))
            if route=='/api/cadres-images.json':
                cookies=self.headers.get('Cookie','')
                actual={c.strip().split('=',1)[1] for c in cookies.split(';') if c.strip().startswith('EkoleTeacher=') and '=' in c}
                if not any(secrets.compare_digest(x,token) for x in actual):return self.respond(401,b'Session Enseignant requise')
                if self.headers.get('Origin')!=f'http://127.0.0.1:{self.server.server_port}':return self.respond(403,b'Origine interdite')
                if not secrets.compare_digest(self.headers.get('X-Ekole-CSRF',''),csrf_token):return self.respond(403,b'Jeton invalide')
                if self.headers.get('Content-Type')!='application/json':return self.respond(415,b'JSON requis')
                length=self.headers.get('Content-Length','')
                if not length.isascii() or not length.isdigit() or not 2<=int(length)<=512:return self.respond(413,b'Configuration trop volumineuse')
                raw=self.rfile.read(int(length))
                if len(raw)!=int(length):return self.respond(400,b'Donnees incompletes')
                try:
                    config=json.loads(raw.decode('utf-8'))
                except (ValueError,UnicodeDecodeError):return self.respond(400,b'JSON invalide')
                if (not isinstance(config,dict) or set(config) not in ({'format','style','size'},{'format','style','size','borderColor'}) or
                    config.get('format')!='ekole.image-frames/1.0' or
                    config.get('style') not in ('epure','carte','galerie','carnet','bandeau','sombre','bordure') or
                    config.get('size') not in ('compact','normal','grand') or
                    ('borderColor' in config and (not isinstance(config['borderColor'],str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',config['borderColor'])))):
                    return self.respond(422,b'Style, taille ou couleur invalides')
                if config['style']=='bordure' and 'borderColor' not in config:
                    config['borderColor']='#1e6864'
                if 'borderColor' in config:config['borderColor']=config['borderColor'].lower()
                dest=root/'site/eleve/data/cadres-images.json'
                folder=dest.parent
                if folder.is_symlink() or dest.is_symlink() or not folder.is_dir() or not folder.resolve().is_relative_to(root.resolve()):
                    return self.respond(403,b'Emplacement de configuration refuse')
                payload=(json.dumps(config,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
                fd,tmp=tempfile.mkstemp(prefix='.cadres-images-',suffix='.json.tmp',dir=folder)
                try:
                    with os.fdopen(fd,'wb') as out:out.write(payload)
                    os.replace(tmp,dest)
                finally:
                    if os.path.exists(tmp):os.unlink(tmp)
                return self.respond(200,payload,'application/json; charset=utf-8')
            match=re.fullmatch(r'/api/visual-upload/(qc-pri-[a-z]+-[0-9]{3})/([a-z][a-z0-9_-]{1,48})',route)
            if not match:return self.respond(404,b'Not found')
            cookies=self.headers.get('Cookie','')
            actual={c.strip().split('=',1)[1] for c in cookies.split(';') if c.strip().startswith('EkoleTeacher=') and '=' in c}
            if not any(secrets.compare_digest(x,token) for x in actual):return self.respond(401,b'Session Enseignant requise')
            expected_origin=f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Origin')!=expected_origin:return self.respond(403,b'Origine interdite')
            if not secrets.compare_digest(self.headers.get('X-Ekole-CSRF',''),csrf_token):return self.respond(403,b'Jeton de session invalide')
            length=self.headers.get('Content-Length','')
            if not length.isascii() or not length.isdigit() or not 20<=int(length)<=12*1024*1024:
                return self.respond(413,b'Fichier trop volumineux ou absent')
            if self.headers.get('Content-Type')!='application/octet-stream':return self.respond(415,b'Envoyer un fichier image brut')
            image_format=self.headers.get('X-Ekole-Format','').lower()
            ext={'webp':'.webp','png':'.png','jpeg':'.jpg'}.get(image_format)
            if not ext:return self.respond(400,b'Format non pris en charge')
            max_width=self.headers.get('X-Ekole-Max-Width','')
            if max_width not in ('768','1024','1536','2048'):return self.respond(400,b'Largeur invalide')
            replace=self.headers.get('X-Ekole-Replace','')=='yes'
            kid,slot=match.groups()
            workspace=root/'kristals'/kid
            manifest=workspace/'experience/RESSOURCES_VISUELLES.json'
            if manifest.is_symlink() or not manifest.is_file():return self.respond(404,b'Kristal source non disponible')
            try:
                cfg=json.loads(manifest.read_text(encoding='utf-8'))
                if cfg.get('format')!='ekole.kristal-visual-layer/1.0' or cfg.get('kristal_id')!=kid or slot not in [x.get('slot') for x in cfg.get('visuels',[])]:
                    return self.respond(422,b'Emplacement inconnu dans le Kristal')
                target_dir=workspace/'experience/images'
                if target_dir.is_symlink() or not target_dir.resolve().is_relative_to(workspace.resolve()):return self.respond(403,b'Chemin image refuse')
                target_dir.mkdir(exist_ok=True)
                if target_dir.is_symlink() or not target_dir.resolve().is_relative_to(workspace.resolve()):return self.respond(403,b'Chemin image refuse')
                from PIL import Image, ImageOps
                raw=self.rfile.read(int(length))
                if len(raw)!=int(length):return self.respond(400,b'Upload incomplet')
                with Image.open(io.BytesIO(raw)) as opened:
                    if opened.format not in ('PNG','JPEG','WEBP') or getattr(opened,'n_frames',1)!=1:
                        return self.respond(415,b'Image PNG, JPEG ou WebP statique requise')
                    w,h=opened.size
                    if w<120 or h<120 or w*h>30_000_000:return self.respond(422,b'Dimensions invalides')
                    opened.load()
                    image=ImageOps.exif_transpose(opened).copy()
                if image.width>int(max_width):
                    target_h=round(image.height*int(max_width)/image.width)
                    if target_h<120:return self.respond(422,b'Image trop aplatie apres ajustement')
                    image=image.resize((int(max_width),target_h),Image.Resampling.LANCZOS)
                if image_format=='jpeg':image=image.convert('RGB')
                elif image_format=='png':image=image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                else:image=image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                fmt={'webp':'WEBP','png':'PNG','jpeg':'JPEG'}[image_format]
                encoded=io.BytesIO()
                image.save(encoded,format=fmt,**({'quality':88,'method':5} if fmt=='WEBP' else {'quality':90,'optimize':True} if fmt=='JPEG' else {'optimize':True}))
                payload=encoded.getvalue()
                if len(payload)>12*1024*1024:return self.respond(413,b'Image ajustee encore trop volumineuse')
                existing=[target_dir/(slot+x) for x in ('.webp','.png','.jpg','.jpeg') if (target_dir/(slot+x)).exists() or (target_dir/(slot+x)).is_symlink()]
                if any(p.is_symlink() for p in existing):return self.respond(403,b'Lien symbolique refuse')
                if existing and not replace:return self.respond(409,b'Une image existe deja. Autoriser explicitement son remplacement.')
                # Prepare complete image before changing any destination file.
                fd,tmp=tempfile.mkstemp(prefix='.ekole-image-',suffix='.tmp',dir=target_dir)
                try:
                    with os.fdopen(fd,'wb') as out:out.write(payload)
                    backups={p:p.read_bytes() for p in existing}
                    target=target_dir/(slot+ext)
                    try:
                        # durable backup is private: outside site/ and the student export
                        if existing:
                            bdir=root/'archives'/'ekole-images'/kid
                            bdir.mkdir(parents=True,exist_ok=True)
                            for old in existing:
                                name=old.name+'.'+secrets.token_hex(6)+'.bak'
                                (bdir/name).write_bytes(backups[old])
                        for old in existing:old.unlink()
                        os.replace(tmp,target)
                        from compiler_visuels_kristals import compile_layer
                        published=compile_layer(root)
                        projected=next(x for x in published['cours'][kid]['visuels'] if x['slot']==slot)
                        if not projected.get('url'):raise RuntimeError('Image non valide dans le compilateur')
                    except Exception:
                        target.unlink(missing_ok=True)
                        for old,data in backups.items():old.write_bytes(data)
                        from compiler_visuels_kristals import compile_layer
                        compile_layer(root)
                        raise
                finally:
                    if os.path.exists(tmp):os.unlink(tmp)
                res={'status':'installed','kristal_id':kid,'slot':slot,'file_name':target.name,'width':image.width,'height':image.height,'size':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'public_url':projected['url']}
                return self.respond(201,(json.dumps(res,ensure_ascii=False)+'\n').encode('utf-8'),'application/json; charset=utf-8')
            except (ValueError,OSError,RuntimeError) as exc:
                return self.respond(422,('Image refusee : '+str(exc)).encode('utf-8'))
            except Exception:
                return self.respond(500,b'Erreur de traitement image : consulter le journal local')
    return Handler

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument('--root',default=None)
    arg.add_argument('--port',type=int,default=8766)
    arg.add_argument('--open',action='store_true')
    args=arg.parse_args();root=pathlib.Path(args.root).resolve() if args.root else ROOT
    if not (root/'enseignant-app/index.html').is_file():raise FileNotFoundError('enseignant-app absent')
    token=secrets.token_urlsafe(32)
    with http.server.ThreadingHTTPServer(('127.0.0.1',args.port),create_handler(root,token)) as server:
        url=f'http://127.0.0.1:{server.server_port}/open?key={token}'
        print('Ekole Enseignant : serveur LOCAL. Ne jamais exposer le port 8766 sur le reseau.',flush=True)
        print('Adresse temporaire : '+url,flush=True)
        if args.open:webbrowser.open(url)
        server.serve_forever()
if __name__=='__main__':main()
