"""Explorateur local de la banque candidate PRF-22, sans modification des sources."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

ROOT=Path(__file__).resolve().parent.parent
REPO_ROOT=ROOT.parents[1]
BANK=Path(os.environ.get('EKOLE_PRF22_BANQUE_ROOT',str(REPO_ROOT/'banques'/'prf22'/('candidats-v0_7' if (REPO_ROOT/'banques'/'prf22'/'candidats-v0_7'/'MANIFEST.json').is_file() else 'candidats-v0_6' if (REPO_ROOT/'banques'/'prf22'/'candidats-v0_6'/'MANIFEST.json').is_file() else 'candidats-v0_4'))))

class Explorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Ékole · Banque de situations PRF-22 (candidates à réviser)')
        self.geometry('1160x720');self.minsize(850,550)
        self.search=tk.StringVar();self.rootvar=tk.StringVar(value=os.environ.get('EKOLE_KONTEXTE_ROOT',r'C:\mycode\Ekole\Kontexte'))
        self.pathvar=tk.StringVar(value=str(BANK))
        self.index=[];self.current={}
        bar=ttk.Frame(self,padding=12);bar.pack(fill='x')
        ttk.Label(bar,text='Banque PRF-22 · Propositions à réviser',font=('Segoe UI',16,'bold')).pack(side='left')
        ttk.Label(bar,text='AUCUNE SÉANCE · AUCUN DROIT',foreground='#96641f').pack(side='right')
        path=ttk.Frame(self,padding=(12,0,12,8));path.pack(fill='x')
        ttk.Label(path,text='Dossier banque :').pack(side='left')
        ttk.Entry(path,textvariable=self.pathvar).pack(side='left',fill='x',expand=True,padx=6)
        ttk.Button(path,text='Charger',command=self.load).pack(side='left')
        kon=ttk.Frame(self,padding=(12,0,12,8));kon.pack(fill='x')
        ttk.Label(kon,text='Racine Kontexte :').pack(side='left')
        ttk.Entry(kon,textvariable=self.rootvar).pack(side='left',fill='x',expand=True,padx=6)
        finder=ttk.Frame(self,padding=(12,0,12,6));finder.pack(fill='x')
        ttk.Label(finder,text='Filtrer par situation, domaine ou référence :').pack(side='left')
        ent=ttk.Entry(finder,textvariable=self.search);ent.pack(side='left',fill='x',expand=True,padx=8)
        self.search.trace_add('write',lambda *_:self.filter())
        pane=ttk.Panedwindow(self,orient='horizontal');pane.pack(fill='both',expand=True,padx=12,pady=8)
        left=ttk.Frame(pane);pane.add(left,weight=3)
        self.tree=ttk.Treeview(left,columns=('domaine','qualite','reference'),show='tree headings',selectmode='browse')
        self.tree.heading('#0',text='Situation');self.tree.column('#0',width=310)
        for name,label,width in [('domaine','Focale',150),('qualite','Revue',130),('reference','Source',210)]:
            self.tree.heading(name,text=label);self.tree.column(name,width=width)
        sy=ttk.Scrollbar(left,orient='vertical',command=self.tree.yview);self.tree.configure(yscrollcommand=sy.set)
        self.tree.pack(side='left',fill='both',expand=True);sy.pack(side='right',fill='y')
        self.tree.bind('<<TreeviewSelect>>',self.show)
        right=ttk.Frame(pane,padding=8);pane.add(right,weight=2)
        ttk.Label(right,text='Fiche de conception',font=('Segoe UI',12,'bold')).pack(anchor='w')
        self.info=tk.Text(right,wrap='word',font=('Segoe UI',10),state='disabled')
        self.info.pack(fill='both',expand=True,pady=8)
        ttk.Button(right,text='Ouvrir dans le compositeur',command=self.open_editor).pack(fill='x',pady=4)
        ttk.Button(right,text='Ouvrir le dossier des documents',command=self.open_folder).pack(fill='x',pady=4)
        ttk.Button(right,text='Vérifier cette proposition',command=self.verify_one).pack(fill='x',pady=4)
        self.status=tk.StringVar(value='Charger la banque préconstruite.');ttk.Label(self,textvariable=self.status,padding=(12,6)).pack(fill='x')
        self.load()

    def load(self):
        try:
            folder=Path(self.pathvar.get()).resolve()
            d=json.loads((folder/'MANIFEST.json').read_text(encoding='utf-8'))
            if d.get('format') not in ('ekole.prf22.banque-candidate/0.4','ekole.prf22.banque-candidate/0.6','ekole.prf22.banque-candidate/0.7'):raise ValueError('Format de banque inconnu')
            for record in d['entries']:
                candidate=Path(record['folder'])
                if candidate.is_absolute() or '..' in candidate.parts or not (folder/candidate).resolve().is_relative_to(folder):
                    raise ValueError('Chemin de banque hors du dossier autorisé')
            self.index=d['entries'];self._folder=folder
            self.filter()
            self.status.set(f"{len(self.index)} propositions • {d['source_situations_covered']} situations sources • brouillons non approuvés")
        except Exception as ex:
            messagebox.showerror('Banque non chargée',str(ex))

    def filter(self):
        q=self.search.get().strip().casefold()
        for node in self.tree.get_children():self.tree.delete(node)
        self.current={}
        for i,rec in enumerate(self.index):
            t=' '.join(str(rec.get(k,'')) for k in ('titre','source_ref','focale','quality')).casefold()
            if q and q not in t:continue
            key=str(i);self.current[key]=rec
            self.tree.insert('', 'end', iid=key,text=rec['titre'],values=(rec['focale'],rec['quality'].replace('REVUE_',''),rec['source_ref']))
        children=self.tree.get_children()
        if children:
            self.tree.selection_set(children[0]);self.show()

    def selected(self):
        s=self.tree.selection()
        if not s: raise ValueError('Choisir une proposition dans la liste')
        return self.current[s[0]]

    def show(self,event=None):
        try:rec=self.selected()
        except ValueError:return
        txt=(f"{rec['titre']}\n\nFocale : {rec['focale']}\nSource Kontexte : {rec['source_ref']}\n"
             f"Statut : {rec['quality']}\n\nACTIVITÉS\n"+'\n'.join('• '+a for a in rec['activity_refs'])+
             '\n\nOBJECTIFS\n'+'\n'.join('• '+a for a in rec['objective_refs'])+
             '\n\nPROVENANCE ET LIMITES\n'+rec['justification_provenance']+
             '\n\nPlans candidats : 1, 8 et 30 enfants. Aucune revue humaine effectuée.\n'
             'La présence de trois postes parallèles pour 30 élèves est hypothétique.')
        sheet=self._folder/rec['folder']/'FICHE_PEDAGOGIQUE.json'
        if sheet.is_file():
            detail=json.loads(sheet.read_text(encoding='utf-8'))
            txt+='\n\nFICHE DE COHÉRENCE\n'
            txt+='Production : '+detail['production_attendue_source']+'\n'
            for a in detail['activites']:
                txt+='\n• '+a['titre']+'\n  Choix : '+a['motif_de_choix']+'\n  Consigne : '+a['consigne_contextualisee']+'\n  Trace : '+a['preuve']+'\n'
            txt+='\nLes liens restent des hypothèses de conception et non des qualifications.\n'
        self.info.configure(state='normal');self.info.delete('1.0','end');self.info.insert('1.0',txt);self.info.configure(state='disabled')

    def open_editor(self):
        try:
            rec=self.selected();path=self._folder/rec['folder']/'brouillon.json'
            if not path.is_file():raise FileNotFoundError(path)
            subprocess.Popen([sys.executable,str(ROOT/'app'/'Atelier_PRF22.pyw'),'--brouillon',str(path),'--kontexte',self.rootvar.get()],cwd=str(ROOT))
            self.status.set('Brouillon ouvert dans un nouvel atelier; aucun document modifié.')
        except Exception as ex:messagebox.showerror('Ouverture',str(ex))

    def open_folder(self):
        try:
            p=self._folder/self.selected()['folder']
            if os.name=='nt':os.startfile(str(p))
            else:messagebox.showinfo('Dossier',str(p))
        except Exception as ex:messagebox.showerror('Dossier',str(ex))

    def verify_one(self):
        try:
            from prf22_validator import validate_document
            rec=self.selected();p=self._folder/rec['folder']/'design.json'
            errors,full=validate_document(json.loads(p.read_text(encoding='utf-8')))
            msg=('Contrat PRF-22 valide.\n'+('JSON Schema intégral vérifié.' if full else 'Sous-ensemble portable vérifié.')+
                 '\n\nLe contenu pédagogique reste à approuver.') if not errors else '\n'.join(errors[:12])
            messagebox.showinfo('Contrôle local' if not errors else 'Contrôle échoué',msg)
        except Exception as ex:messagebox.showerror('Contrôle',str(ex))

if __name__=='__main__':Explorer().mainloop()
