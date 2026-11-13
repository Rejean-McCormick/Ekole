"""Interface enseignant : compositeur local de situations pédagogiques.

Aucun accès réseau, aucun compte enfant et aucune admission Orgo.
"""
from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from pathlib import Path
import json

from prf22_workspace import materialize
from prf22_core import (build_design, authoring_state, load_authoring, export_pack,
                        VALID_THEORY_IDS, LEARNING_TYPES, FOURCID_COMPONENTS)

from composer_core import PREFERRED_KONTEXTE, compose_draft, export_activity_index, export_draft, format_preview, load_catalogue


class Application(tk.Tk):
    def __init__(self, initial_file=None, source_root=None):
        super().__init__()
        self.title("Ékole · Atelier PRF-22 (intégré au dépôt Ékole)")
        self.geometry("1220x790")
        self.minsize(1000, 650)
        self.catalog = None
        self.template_refs = []
        self.filtered_activity_refs = []
        self.filtered_objective_refs = []
        self.selected_activities: list[str] = []
        self.selected_objectives: list[str] = []
        self.draft = None
        self.theory_entries = {}
        self.current_objective = None
        self._theory_activity_refs = []
        self.path = tk.StringVar(value=source_root or os.environ.get("EKOLE_KONTEXTE_ROOT", str(PREFERRED_KONTEXTE)))
        self.template_var = tk.StringVar()
        self.epoch_var = tk.StringVar(value="Québec contemporain")
        self.culture_var = tk.StringVar(value="Milieu local choisi avec la classe")
        self.place_var = tk.StringVar(value="Village fictif et salle de classe")
        self.reality_var = tk.StringVar(value="fictif")
        self.language_var = tk.StringVar(value="fr-CA")
        self.participants_var = tk.IntVar(value=24)
        self.group_size_var = tk.IntVar(value=4)
        self.parallel_posts_var = tk.IntVar(value=1)
        self.activity_search = tk.StringVar()
        self.objective_search = tk.StringVar()
        self.status_var = tk.StringVar(value="Choisir les sources Kontexte.")
        self.configure(bg="#f7f9fc")
        self._build()
        self._load()
        if initial_file:
            self._open_authoring(initial_file)

    def _label(self, parent, text, row, column, **kwargs):
        return ttk.Label(parent, text=text).grid(row=row, column=column, sticky="w", padx=7, pady=7, **kwargs)

    def _build(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("TNotebook.Tab", padding=(15, 10))
        bar = ttk.Frame(self, padding=10)
        bar.pack(fill="x")
        ttk.Label(bar, text="Ékole · Compositeur PRF-22", font=("Segoe UI", 18, "bold")).pack(side="left", padx=(3, 20))
        ttk.Label(bar, text="BROUILLON — aucune séance réelle", foreground="#855c1f").pack(side="right")
        source = ttk.Frame(self, padding=(15, 3, 15, 5))
        source.pack(fill="x")
        ttk.Label(source, text="Dépôt Kontexte :").pack(side="left", padx=(0, 8))
        ttk.Entry(source, textvariable=self.path, width=85).pack(side="left", fill="x", expand=True)
        ttk.Button(source, text="Parcourir", command=self._choose_root).pack(side="left", padx=(8, 5))
        ttk.Button(source, text="Charger", command=self._load).pack(side="left")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=10)
        self.tab_scene = ttk.Frame(self.notebook, padding=16)
        self.tab_ex = ttk.Frame(self.notebook, padding=16)
        self.tab_objectives = ttk.Frame(self.notebook, padding=16)
        self.tab_org = ttk.Frame(self.notebook, padding=16)
        self.tab_theory = ttk.Frame(self.notebook, padding=16)
        self.tab_preview = ttk.Frame(self.notebook, padding=16)
        for label, tab in [("1 · Situation",self.tab_scene),("2 · Exercices",self.tab_ex),
                           ("3 · Objectifs",self.tab_objectives),("4 · Organisation 1 à 30",self.tab_org),
                           ("5 · Théorie et preuves",self.tab_theory), ("6 · Vérification et export",self.tab_preview)]:
            self.notebook.add(tab, text=label)
        self._scene_tab(); self._exercise_tab(); self._objective_tab(); self._org_tab(); self._theory_tab(); self._preview_tab()
        foot = ttk.Frame(self, padding=(15, 8))
        foot.pack(fill="x")
        ttk.Label(foot, textvariable=self.status_var).pack(side="left", fill="x", expand=True)
        ttk.Button(foot, text="Construire l'aperçu", command=self._preview).pack(side="right", padx=4)
        ttk.Button(foot, text="Exporter le répertoire", command=self._export_index).pack(side="right", padx=4)
        ttk.Button(foot, text="Exporter dossier PRF-22", command=self._export).pack(side="right", padx=4)
        ttk.Button(foot, text="Enregistrer brouillon", command=self._save_authoring).pack(side="right", padx=4)
        ttk.Button(foot, text="Ouvrir brouillon", command=self._open_authoring).pack(side="right", padx=4)
        ttk.Button(foot, text="Créer workspace Kristal", command=self._make_workspace).pack(side="right", padx=4)

    def _scene_tab(self):
        frame = self.tab_scene
        frame.columnconfigure(1, weight=1)
        ttk.Label(frame, text="Partir d'une trame ou d'une mission existante", font=("Segoe UI", 13, "bold")).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,14))
        self._label(frame,"Situation source",1,0)
        self.template_choice = ttk.Combobox(frame,textvariable=self.template_var, state="readonly",width=96)
        self.template_choice.grid(row=1,column=1,sticky="ew",padx=7,pady=7)
        self.template_choice.bind("<<ComboboxSelected>>",lambda e:self._scene_info())
        self.scene_info = tk.Text(frame, height=7, wrap="word",font=("Segoe UI", 11),state="disabled",background="#f0f4f9")
        self.scene_info.grid(row=2,column=0,columnspan=2,sticky="ew",padx=7,pady=(2,12))
        ttk.Separator(frame,orient="horizontal").grid(row=3,column=0,columnspan=2,sticky="ew",pady=9)
        self._label(frame,"Époque / temporalité",4,0)
        ttk.Entry(frame,textvariable=self.epoch_var).grid(row=4,column=1,sticky="ew",padx=7,pady=7)
        self._label(frame,"Contexte culturel (à valider)",5,0)
        ttk.Entry(frame,textvariable=self.culture_var).grid(row=5,column=1,sticky="ew",padx=7,pady=7)
        self._label(frame,"Lieu et cadre",6,0)
        ttk.Entry(frame,textvariable=self.place_var).grid(row=6,column=1,sticky="ew",padx=7,pady=7)
        self._label(frame,"Type d'univers",7,0)
        ttk.Combobox(frame,textvariable=self.reality_var,values=["fictif","réel","mixte"],state="readonly",width=17).grid(row=7,column=1,sticky="w",padx=7,pady=7)
        self._label(frame,"Langue",8,0)
        ttk.Combobox(frame,textvariable=self.language_var,values=["fr-CA","en-CA"],state="readonly",width=17).grid(row=8,column=1,sticky="w",padx=7,pady=7)
        ttk.Label(frame,text="Une époque ou une culture ne change pas automatiquement la justesse historique ou les droits culturels. Révision humaine obligatoire.",foreground="#6a5534",wraplength=850).grid(row=9,column=0,columnspan=2,sticky="w",padx=7,pady=12)

    def _exercise_tab(self):
        frame=self.tab_ex
        ttk.Label(frame,text="Répertoire indépendant d'exercices et de micro-situations",font=("Segoe UI",13,"bold")).pack(anchor="w")
        ttk.Label(frame,text="Les micro-situations sont des propositions à instancier; les exercices déterministes sont des fixtures locales, pas des évaluations officielles.",wraplength=1000).pack(anchor="w",pady=(3,12))
        line=ttk.Frame(frame);line.pack(fill="x")
        ttk.Label(line,text="Rechercher :").pack(side="left",padx=(0,6))
        ttk.Entry(line,textvariable=self.activity_search,width=55).pack(side="left",fill="x",expand=True)
        self.activity_search.trace_add("write",lambda *_:self._filter_activities())
        central=ttk.Frame(frame);central.pack(fill="both",expand=True,pady=10)
        central.columnconfigure(0,weight=2);central.columnconfigure(2,weight=2);central.rowconfigure(1,weight=1)
        ttk.Label(central,text="Banque existante").grid(row=0,column=0,sticky="w")
        ttk.Label(central,text="Exercices choisis — stations").grid(row=0,column=2,sticky="w")
        self.available_activities=tk.Listbox(central,selectmode="extended",font=("Segoe UI",10),exportselection=False)
        self.available_activities.grid(row=1,column=0,sticky="nsew",padx=(0,5))
        actions=ttk.Frame(central);actions.grid(row=1,column=1,padx=8)
        ttk.Button(actions,text="Ajouter →",command=self._add_activities).pack(pady=5)
        ttk.Button(actions,text="← Retirer",command=self._remove_activities).pack(pady=5)
        self.selected_activity_list=tk.Listbox(central,selectmode="extended",font=("Segoe UI",10),exportselection=False)
        self.selected_activity_list.grid(row=1,column=2,sticky="nsew",padx=(5,0))
        self.activity_info=ttk.Label(frame,text="Sélectionnez de 1 à 12 activités réutilisables.",wraplength=1000)
        self.activity_info.pack(anchor="w")
        self.available_activities.bind("<<ListboxSelect>>",self._activity_info)

    def _objective_tab(self):
        frame=self.tab_objectives
        ttk.Label(frame,text="Objectifs d'apprentissage (distincts des exercices)",font=("Segoe UI",13,"bold")).pack(anchor="w")
        ttk.Label(frame,text="Liens proposés seulement : un Kristal n'est ni un exercice ni une preuve de maîtrise. L'enseignant valide les correspondances.",wraplength=1000).pack(anchor="w",pady=(3,12))
        line=ttk.Frame(frame);line.pack(fill="x")
        ttk.Label(line,text="Rechercher :").pack(side="left",padx=(0,6))
        ttk.Entry(line,textvariable=self.objective_search,width=55).pack(side="left",fill="x",expand=True)
        self.objective_search.trace_add("write",lambda *_:self._filter_objectives())
        central=ttk.Frame(frame);central.pack(fill="both",expand=True,pady=10)
        central.columnconfigure(0,weight=2);central.columnconfigure(2,weight=2);central.rowconfigure(1,weight=1)
        ttk.Label(central,text="Référentiel existant").grid(row=0,column=0,sticky="w")
        ttk.Label(central,text="Objectifs candidats").grid(row=0,column=2,sticky="w")
        self.available_objectives=tk.Listbox(central,selectmode="extended",font=("Segoe UI",10),exportselection=False)
        self.available_objectives.grid(row=1,column=0,sticky="nsew",padx=(0,5))
        actions=ttk.Frame(central);actions.grid(row=1,column=1,padx=8)
        ttk.Button(actions,text="Associer →",command=self._add_objectives).pack(pady=5)
        ttk.Button(actions,text="← Retirer",command=self._remove_objectives).pack(pady=5)
        self.selected_objective_list=tk.Listbox(central,selectmode="extended",font=("Segoe UI",10),exportselection=False)
        self.selected_objective_list.grid(row=1,column=2,sticky="nsew",padx=(5,0))
        self.objective_info=ttk.Label(frame,text="Les correspondances ne sont pas automatiquement approuvées.",wraplength=1000)
        self.objective_info.pack(anchor="w")
        self.available_objectives.bind("<<ListboxSelect>>",self._objective_info)

    def _org_tab(self):
        frame=self.tab_org
        frame.columnconfigure(1,weight=1)
        ttk.Label(frame,text="Planifier 1 à 30 participants sans figer les rôles",font=("Segoe UI",13,"bold")).grid(row=0,column=0,columnspan=2,sticky="w",pady=(0,14))
        self._label(frame,"Nombre de participants",1,0)
        ttk.Spinbox(frame,from_=1,to=30,textvariable=self.participants_var,width=10).grid(row=1,column=1,sticky="w",padx=7,pady=7)
        self._label(frame,"Taille maximale d'équipe",2,0)
        ttk.Spinbox(frame,from_=1,to=6,textvariable=self.group_size_var,width=10).grid(row=2,column=1,sticky="w",padx=7,pady=7)
        self._label(frame,"Postes parallèles par exercice",3,0)
        ttk.Spinbox(frame,from_=1,to=10,textvariable=self.parallel_posts_var,width=10).grid(row=3,column=1,sticky="w",padx=7,pady=7)
        ttk.Button(frame,text="Calculer les rotations",command=self._preview).grid(row=4,column=0,columnspan=2,sticky="w",padx=7,pady=14)
        ttk.Label(frame,text="Les stations proviennent des activités choisies. Chaque équipe les visite une fois. Plusieurs postes parallèles réduisent l’attente si le matériel est disponible.",wraplength=890).grid(row=5,column=0,columnspan=2,sticky="w",padx=7,pady=9)
        ttk.Label(frame,text="Les rôles sont suggérés par équipe (identifiants Kontexte), jamais attribués à de vrais élèves ni confondus avec les permissions Orgo.",wraplength=890).grid(row=6,column=0,columnspan=2,sticky="w",padx=7,pady=9)
        ttk.Label(frame,text="Solo : l'enseignant ou le matériel remplace les partenaires absents. Grand groupe : postes multiples, rotations et tâches autonomes.",wraplength=890).grid(row=7,column=0,columnspan=2,sticky="w",padx=7,pady=9)

    def _preview_tab(self):
        ttk.Label(self.tab_preview,text="Aperçu pédagogique et logistique (sans admission réelle)",font=("Segoe UI",13,"bold")).pack(anchor="w",pady=(0,8))
        self.preview_box=tk.Text(self.tab_preview,wrap="word",font=("Consolas",10),background="#f9fafb",state="disabled")
        self.preview_box.pack(fill="both",expand=True)

    def _theory_tab(self):
        frame=self.tab_theory
        ttk.Label(frame,text="Carte de cohérence : objectif → hypothèse → activité → processus → preuve",font=("Segoe UI",13,"bold")).pack(anchor="w")
        ttk.Label(frame,text="Chaque objectif choisi exige une carte argumentée. Sources théoriques = références de conception, pas certification. Tous les champs sont enregistrables même incomplets.",wraplength=1050).pack(anchor="w",pady=(4,9))
        selector=ttk.Frame(frame);selector.pack(fill="x",pady=(0,8))
        ttk.Label(selector,text="Objectif à documenter :").pack(side="left",padx=(0,8))
        self.theory_objective_choice=ttk.Combobox(selector,state="readonly",width=85)
        self.theory_objective_choice.pack(side="left",fill="x",expand=True)
        self.theory_objective_choice.bind("<<ComboboxSelected>>",lambda _:self._switch_objective())
        ttk.Button(selector,text="Mémoriser cette carte",command=self._save_current_theory).pack(side="left",padx=8)
        notebook=ttk.Notebook(frame);notebook.pack(fill="both",expand=True)
        self.theory_tab_hyp=ttk.Frame(notebook,padding=9)
        self.theory_tab_evidence=ttk.Frame(notebook,padding=9)
        self.theory_tab_links=ttk.Frame(notebook,padding=9)
        notebook.add(self.theory_tab_hyp,text="Hypothèse et mécanisme")
        notebook.add(self.theory_tab_evidence,text="Preuves, critères et limites")
        notebook.add(self.theory_tab_links,text="Liaisons et dépendances")
        self.theory_fields={}
        def add_fields(parent,items):
            parent.columnconfigure(1,weight=1)
            for i,(field,label) in enumerate(items):
                ttk.Label(parent,text=label,wraplength=230).grid(row=i,column=0,sticky="nw",padx=6,pady=7)
                txt=tk.Text(parent,height=2,wrap="word",font=("Segoe UI",10),undo=True)
                txt.grid(row=i,column=1,sticky="ew",padx=6,pady=5)
                self.theory_fields[field]=txt
        add_fields(self.theory_tab_hyp,[("conjecture_statement","Hypothèse : pourquoi cela aiderait-il ?"),
              ("expected_action","Action observable de l'enfant"),
              ("process","Processus d'apprentissage attendu"),
              ("observation","Comment observer le processus ?"),
              ("boundary","Conditions de fonctionnement / prérequis")])
        add_fields(self.theory_tab_evidence,[("evidence","Preuve ou production attendue"),
              ("criterion","Critères de jugement par l'enseignant"),
              ("disconfirmation","Ce qui contredirait l'hypothèse"),
              ("alternative","Une explication alternative possible"),
              ("interpretation_limit","Limites de la preuve (individuel / collectif)")])
        link=self.theory_tab_links
        link.columnconfigure(1,weight=1)
        ttk.Label(link,text="Activités qui servent cet objectif").grid(row=0,column=0,sticky="nw",padx=8,pady=6)
        self.theory_activity_list=tk.Listbox(link,selectmode="multiple",height=6,exportselection=False, font=("Segoe UI",10))
        self.theory_activity_list.grid(row=0,column=1,sticky="ew",padx=8,pady=6)
        ttk.Label(link,text="Références théoriques").grid(row=1,column=0,sticky="nw",padx=8,pady=6)
        self.theory_sources=tk.Listbox(link,selectmode="multiple",height=6,exportselection=False, font=("Segoe UI",10))
        self.theory_sources.grid(row=1,column=1,sticky="ew",padx=8,pady=6)
        for tid in VALID_THEORY_IDS:self.theory_sources.insert("end",tid)
        ttk.Label(link,text="Évaluation").grid(row=2,column=0,sticky="w",padx=8,pady=6)
        self.peer_var=tk.StringVar(value="individual_possible")
        ttk.Combobox(link,state="readonly",textvariable=self.peer_var,
                     values=["individual_possible","peer_interaction"],width=25).grid(row=2,column=1,sticky="w",padx=8,pady=6)
        ttk.Label(link,text="Type d'apprentissage").grid(row=3,column=0,sticky="w",padx=8,pady=6)
        self.learning_type_var=tk.StringVar(value="practice")
        ttk.Combobox(link,state="readonly",textvariable=self.learning_type_var,
                     values=list(LEARNING_TYPES),width=25).grid(row=3,column=1,sticky="w",padx=8,pady=6)
        ttk.Label(link,text="4C/ID : composante candidate").grid(row=4,column=0,sticky="w",padx=8,pady=6)
        self.fourcid_var=tk.StringVar(value="none")
        ttk.Combobox(link,state="readonly",textvariable=self.fourcid_var,
                     values=list(FOURCID_COMPONENTS),width=25).grid(row=4,column=1,sticky="w",padx=8,pady=6)
        ttk.Label(link,text="Durée indicative (min.)").grid(row=5,column=0,sticky="w",padx=8,pady=6)
        self.duration_var=tk.IntVar(value=15)
        ttk.Spinbox(link,from_=1,to=180,textvariable=self.duration_var,width=10).grid(row=5,column=1,sticky="w",padx=8,pady=6)
        ttk.Label(link,text="Dépendances entre activités (réf avant > réf après : production) :").grid(row=6,column=0,sticky="nw",padx=8,pady=6)
        self.deps_text=tk.Text(link,height=4,font=("Consolas",10),wrap="word")
        self.deps_text.grid(row=6,column=1,sticky="ew",padx=8,pady=6)
        ttk.Label(link,text="L'identité des personnes, les résultats réels et les autorisations restent hors du Kristal.",wraplength=980).grid(row=7,column=0,columnspan=2,sticky="w",padx=8,pady=6)

    def _save_current_theory(self):
        ref=self.current_objective
        if not ref:return
        mapping=dict(self.theory_entries.get(ref,{}))
        for key,widget in self.theory_fields.items():
            mapping[key]=widget.get("1.0","end").strip()
        mapping['activity_refs']=[self._theory_activity_refs[i] for i in self.theory_activity_list.curselection() if i<len(self._theory_activity_refs)]
        mapping['theory_ids']=[VALID_THEORY_IDS[i] for i in self.theory_sources.curselection()]
        mapping['assessment_requires']=self.peer_var.get()
        mapping['learning_type']=self.learning_type_var.get()
        mapping['fourcid_component']=self.fourcid_var.get()
        mapping['duration_minutes']=int(self.duration_var.get())
        self.theory_entries[ref]=mapping
        self.status_var.set('Carte mémorisée : '+ref)

    def _refresh_theory_objectives(self):
        if not hasattr(self,'theory_objective_choice') or not self.catalog:return
        previous=self.current_objective
        if previous:
            self._save_current_theory()
        self.theory_objective_choice['values']=[f"{r} — {self.catalog.objective(r)['titre']}" for r in self.selected_objectives]
        self._theory_activity_refs=list(self.selected_activities)
        for old_ref in list(self.theory_entries):
            if old_ref not in self.selected_objectives:del self.theory_entries[old_ref]
        self.theory_activity_list.delete(0,'end')
        for a in self.selected_activities:
            self.theory_activity_list.insert('end',f"{a} · {self.catalog.activity(a)['titre'][:90]}")
        if self.selected_objectives:
            next_ref=previous if previous in self.selected_objectives else self.selected_objectives[0]
            self.theory_objective_choice.current(self.selected_objectives.index(next_ref))
            self.current_objective=None
            self._switch_objective()
        else:
            self.current_objective=None
            self.theory_objective_choice.set('')
            for widget in self.theory_fields.values():widget.delete('1.0','end')

    def _switch_objective(self):
        if self.current_objective:self._save_current_theory()
        idx=self.theory_objective_choice.current()
        self.current_objective=self.selected_objectives[idx] if idx>=0 and idx<len(self.selected_objectives) else None
        info=self.theory_entries.get(self.current_objective,{})
        for key,widget in self.theory_fields.items():
            widget.delete('1.0','end');widget.insert('1.0',info.get(key,''))
        self.theory_activity_list.selection_clear(0,'end')
        for i,ref in enumerate(self.selected_activities):
            if ref in info.get('activity_refs',[]):self.theory_activity_list.selection_set(i)
        self.theory_sources.selection_clear(0,'end')
        for i,ref in enumerate(VALID_THEORY_IDS):
            if ref in info.get('theory_ids',[]):self.theory_sources.selection_set(i)
        self.peer_var.set(info.get('assessment_requires','individual_possible'))
        self.learning_type_var.set(info.get('learning_type','practice'))
        self.fourcid_var.set(info.get('fourcid_component','none'))
        self.duration_var.set(int(info.get('duration_minutes',15)))

    def _choose_root(self):
        p=filedialog.askdirectory(title="Dossier racine de Kontexte",initialdir=self.path.get())
        if p:
            self.path.set(p);self._load()

    def _load(self):
        try:
            from composer_core import attach_ekole_activity_patterns
            self.catalog=attach_ekole_activity_patterns(load_catalogue(Path(self.path.get())))
        except Exception as exc:
            self.catalog=None
            self.status_var.set("Sources non chargées : " + str(exc))
            messagebox.showerror("Sources Kontexte",str(exc))
            return
        self.template_refs=[x["ref"] for x in self.catalog.templates]
        self.template_choice["values"]=[f"{t['titre']}  [{t['ref']}]" for t in self.catalog.templates]
        self.template_choice.current(next((i for i,x in enumerate(self.template_refs) if x=="mission:fete-sorciere"),0))
        self._scene_info();self._filter_activities();self._filter_objectives();self._refresh_theory_objectives()
        self.status_var.set(f"Chargé : {self.catalog.trames_count} trames, {self.catalog.missions_count} missions, {len(self.catalog.activities)} activités, {len(self.catalog.objectives)} objectifs, {len(self.catalog.roles)} rôles.")

    def _scene_info(self):
        if not self.catalog or self.template_choice.current()<0:
            return
        t=self.catalog.template(self.template_refs[self.template_choice.current()])
        summary=f"{t['titre']}\n\nDéclencheur : {t['declencheur']}\n\nProblème : {t['probleme']}\n\nPersonnages suggérés : {', '.join(t['roles']) or 'à définir'}\nSource : {t['source_relpath']}"
        self.scene_info.configure(state="normal")
        self.scene_info.delete("1.0","end");self.scene_info.insert("1.0",summary)
        self.scene_info.configure(state="disabled")

    def _filter_activities(self):
        if not self.catalog:return
        needle=self.activity_search.get().casefold().strip()
        found=[x for x in self.catalog.activities if needle in (x['titre']+' '+x['domaine']+' '+x['source_type']).casefold()]
        self.filtered_activity_refs=[x['ref'] for x in found]
        self.available_activities.delete(0,"end")
        for x in found:
            self.available_activities.insert("end",f"[{x['source_type']}] {x['titre']}")

    def _filter_objectives(self):
        if not self.catalog:return
        needle=self.objective_search.get().casefold().strip()
        found=[x for x in self.catalog.objectives if needle in (x['titre']+' '+x['discipline']+' '+x['objectif']+' '+x['ref']).casefold()]
        self.filtered_objective_refs=[x['ref'] for x in found]
        self.available_objectives.delete(0,"end")
        for x in found:
            self.available_objectives.insert("end",f"{x['ref']} · {x['titre']}")

    def _activity_info(self,event=None):
        if not self.available_activities.curselection():return
        idx=self.available_activities.curselection()[0]
        ex=self.catalog.activity(self.filtered_activity_refs[idx])
        self.activity_info.configure(text=f"{ex['source_type']} · {ex['qualification']}  —  {ex['consigne']}  —  Preuve : {ex['preuve_attendue']}")

    def _objective_info(self,event=None):
        if not self.available_objectives.curselection():return
        idx=self.available_objectives.curselection()[0]
        o=self.catalog.objective(self.filtered_objective_refs[idx])
        self.objective_info.configure(text=f"{o['ref']} · {o['source_status']}  —  {o['objectif']}  —  Preuve envisagée : {o['preuve_attendue']}")

    def _add_activities(self):
        for i in self.available_activities.curselection():
            ref=self.filtered_activity_refs[i]
            if ref not in self.selected_activities and len(self.selected_activities)<12:
                self.selected_activities.append(ref)
        self._refresh_selected()

    def _remove_activities(self):
        remove={self.selected_activities[i] for i in self.selected_activity_list.curselection()}
        self.selected_activities=[ref for ref in self.selected_activities if ref not in remove]
        self._refresh_selected()

    def _add_objectives(self):
        for i in self.available_objectives.curselection():
            ref=self.filtered_objective_refs[i]
            if ref not in self.selected_objectives and len(self.selected_objectives)<20:
                self.selected_objectives.append(ref)
        self._refresh_selected()

    def _remove_objectives(self):
        remove={self.selected_objectives[i] for i in self.selected_objective_list.curselection()}
        self.selected_objectives=[ref for ref in self.selected_objectives if ref not in remove]
        self._refresh_selected()

    def _refresh_selected(self):
        self.selected_activity_list.delete(0,"end")
        for ref in self.selected_activities:
            self.selected_activity_list.insert("end",self.catalog.activity(ref)["titre"])
        self.selected_objective_list.delete(0,"end")
        for ref in self.selected_objectives:
            o=self.catalog.objective(ref)
            self.selected_objective_list.insert("end",f"{o['ref']} · {o['titre']}")
        if hasattr(self,"theory_objective_choice"):
            self._refresh_theory_objectives()

    def _construct(self):
        if not self.catalog:raise ValueError("Kontexte non chargé")
        index=self.template_choice.current()
        if index<0:raise ValueError("Choisis une situation")
        return compose_draft(
            self.catalog, source_ref=self.template_refs[index],activities=self.selected_activities,
            participants=int(self.participants_var.get()),maximum_per_team=int(self.group_size_var.get()),
            epoch=self.epoch_var.get(),cultural_frame=self.culture_var.get(),setting=self.place_var.get(),
            reality=self.reality_var.get(),language=self.language_var.get(),
            objectives=self.selected_objectives,parallel_posts=int(self.parallel_posts_var.get()),
        )

    def _preview(self):
        try:
            self.draft=self._construct()
            txt=format_preview(self.draft)
            self._save_current_theory()
            try:
                design=build_design(self.draft, self.theory_entries, self.deps_text.get("1.0","end").strip())
            except Exception as exc:
                txt += "\nPRF-22 — CONTRÔLE INCOMPLET :\n" + str(exc) + "\n"
            else:
                txt += "\nPRF-22 — STRUCTURE ET ALIGNEMENTS CONFORMES\n"
                txt += f"{len(design['pedagogical_model']['conjectures'])} conjecture(s), {len(design['pedagogical_model']['alignment'])} lien(s) d'alignement.\n"
                txt += "Aucune évaluation pédagogique ni activation effectuée.\n"
        except Exception as exc:
            messagebox.showwarning("Plan incomplet",str(exc));return
        self.preview_box.configure(state="normal")
        self.preview_box.delete("1.0","end");self.preview_box.insert("1.0",txt)
        self.preview_box.configure(state="disabled")
        self.notebook.select(self.tab_preview)
        self.status_var.set("Aperçu généré — plan local uniquement, aucune tâche Orgo créée.")

    def _export_index(self):
        if not self.catalog:
            messagebox.showwarning("Catalogue", "Charger d'abord Kontexte.")
            return
        folder=filedialog.askdirectory(title="Où exporter le répertoire d'activités ?",initialdir=str(Path.home()/"Documents"))
        if not folder:
            return
        try:
            path=export_activity_index(self.catalog,folder)
        except Exception as exc:
            messagebox.showerror("Export du répertoire",str(exc))
            return
        self.status_var.set("Répertoire d'activités exporté : "+str(path))
        messagebox.showinfo("Répertoire exporté",str(path)+"\n\nAucune réponse d'exercice publiée.")

    def _make_workspace(self):
        try:
            self._save_current_theory()
            draft=self._construct()
            design=build_design(draft,self.theory_entries,self.deps_text.get('1.0','end').strip())
        except Exception as exc:
            self.notebook.select(self.tab_theory)
            messagebox.showwarning('PRF-22 incomplet',str(exc));return
        parent=filedialog.askdirectory(title='Dossier parent du nouveau workspace Kristal')
        if not parent:return
        slug=simpledialog.askstring('Nom technique','Slug du workspace, ex. fete-sorciere-prf22 :',parent=self)
        if not slug:return
        default_root=Path(os.environ.get('EKOLE_ARKETYPE_ROOT',r'C:\mycode\Kristal\Arketype'))
        if default_root.exists():root=default_root
        else:
            selected=filedialog.askdirectory(title='Choisir le dépôt Arketype')
            if not selected:return
            root=Path(selected)
        try:
            preview=materialize(design,root,Path(parent),slug,dry_run=True)
        except Exception as exc:
            messagebox.showerror('Précontrôle Arketype',str(exc));return
        msg=f"Créer le workspace local suivant ?\n\n{preview['destination']}\n\nIl restera non canonique et non publié. Aucune séance ou autorisation ne sera créée."
        if not messagebox.askyesno('Action explicite — Kristal local',msg):return
        try:
            result=materialize(design,root,Path(parent),slug,dry_run=False)
        except Exception as exc:
            messagebox.showerror('Création Kristal',str(exc));return
        self.status_var.set('Workspace local créé : '+result['destination'])
        messagebox.showinfo('Kristal local créé',result['destination']+'\n\nContenu de conception seulement; aucune identité canonique ni publication.')

    def _save_authoring(self):
        try:
            self._save_current_theory()
            draft = self._construct()
            data = authoring_state(draft,self.theory_entries,self.deps_text.get("1.0","end").strip(),self.catalog.root)
        except Exception as exc:
            messagebox.showwarning("Brouillon incomplet",str(exc));return
        path=filedialog.asksaveasfilename(title="Enregistrer le brouillon de travail",defaultextension=".json",
                                         filetypes=[("PRF-22 JSON", "*.json")],
                                         initialfile="brouillon-prf22-v03.json")
        if not path:return
        try:
            with open(path,"x",encoding="utf-8") as f:
                json.dump(data,f,ensure_ascii=False,indent=2);f.write("\n")
        except FileExistsError:
            messagebox.showwarning("Brouillon existant","Ce fichier existe déjà. Choisis un nouveau nom pour conserver les versions.");return
        except Exception as exc:
            messagebox.showerror("Écriture impossible",str(exc));return
        self.status_var.set("Brouillon conservé : "+path)

    def _open_authoring(self, path=None):
        if path is None:
            path=filedialog.askopenfilename(title="Ouvrir un brouillon PRF-22",filetypes=[("PRF-22 JSON","*.json")])
        if not path:return
        try:
            record=load_authoring(path)
            d=record['draft'];s=d['source'];ctx=d['world_context'];part=d['participation']
            if not self.catalog:raise ValueError("Charger d'abord Kontexte")
            if s['reference'] not in self.template_refs:
                raise ValueError('Source de situation non présente dans le catalogue actuel')
            for item in d['activity_bindings']:self.catalog.activity(item['activity_ref'])
            for item in d['learning_objective_links']:self.catalog.objective(item['objective_ref'])
            if record.get('source_observations'):
                from prf22_core import observe_catalogue_sources
                observed = observe_catalogue_sources(self.catalog.root,d)
                by_path={v['relative_path']:v['observed_sha256'] for v in observed}
                for item in record['source_observations']:
                    if by_path.get(item.get('relative_path'))!=item.get('observed_sha256'):
                        raise ValueError('Source Kontexte modifiée depuis ce brouillon : '+str(item.get('relative_path')))
            self.template_choice.current(self.template_refs.index(s['reference']))
            self._scene_info()
            self.epoch_var.set(ctx['epoch']);self.culture_var.set(ctx['cultural_frame'])
            self.place_var.set(ctx['place']);self.reality_var.set(ctx['reality']);self.language_var.set(ctx['language'])
            self.participants_var.set(part['participant_count']);self.group_size_var.set(part['maximum_per_team'])
            self.parallel_posts_var.set(part['parallel_posts_per_activity'])
            self.selected_activities=[x['activity_ref'] for x in d['activity_bindings']]
            self.selected_objectives=[x['objective_ref'] for x in d['learning_objective_links']]
            self.theory_entries=record['theory_entries']
            self.current_objective=None
            self.deps_text.delete('1.0','end');self.deps_text.insert('1.0',record['dependency_lines'])
            self._refresh_selected();self._refresh_theory_objectives()
            self.status_var.set("Brouillon de travail rouvert : "+str(path))
        except Exception as exc:
            messagebox.showerror("Ouverture refusée",str(exc))

    def _export(self):
        try:
            self._save_current_theory()
            draft=self._construct()
            design=build_design(draft,self.theory_entries,self.deps_text.get('1.0','end').strip())
        except Exception as exc:
            self.notebook.select(self.tab_theory)
            messagebox.showwarning("Contrôle PRF-22 incomplet",str(exc));return
        folder=filedialog.askdirectory(title="Où exporter le dossier PRF-22 ?",initialdir=str(Path.home()/"Documents"))
        if not folder:return
        try:
            target=export_pack(folder,design,draft,self.theory_entries,
                               self.deps_text.get('1.0','end').strip(), self.catalog.root)
        except Exception as exc:
            messagebox.showerror("Export PRF-22",str(exc));return
        self.status_var.set("Dossier de conception : "+str(target))
        messagebox.showinfo("Dossier exporté",str(target)+"\n\nAucune séance ni permission créée.")


if __name__ == "__main__":
    try:
        import argparse
        ap=argparse.ArgumentParser(description="Atelier PRF-22 — brouillon de conception")
        ap.add_argument("--brouillon",type=Path)
        ap.add_argument("--kontexte",type=Path)
        args=ap.parse_args()
        Application(args.brouillon, str(args.kontexte) if args.kontexte else None).mainloop()
    except Exception as e:
        # .pyw has no console on Windows; expose startup exceptions visibly.
        import traceback
        tmp=tk.Tk();tmp.withdraw()
        messagebox.showerror("Compositeur Ékole",traceback.format_exc())
        tmp.destroy()
        raise
