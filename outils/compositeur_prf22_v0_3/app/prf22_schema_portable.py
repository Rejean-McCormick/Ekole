"""Portable PRF-22 local subset validator, no dependency.

The v0.3 bundled contract uses only the keywords implemented here. This is NOT a
full JSON Schema 2020-12 implementation and MUST NOT be presented as such.
"""
from __future__ import annotations
import re

SUPPORTED={'$schema','$id','$defs','title','type','const','enum','required','properties',
           'additionalProperties','items','minLength','minItems','minimum','maximum',
           'pattern','$ref','allOf','if','then'}


def _schema_keywords(node):
    if not isinstance(node,dict):return []
    # Walk only schema nodes; property names are not JSON Schema keywords.
    found=list(node)
    for k in ('properties','$defs'):
        for sub in node.get(k,{}).values():found+=_schema_keywords(sub)
    for k in ('items','if','then'):
        if isinstance(node.get(k),dict):found+=_schema_keywords(node[k])
    for sub in node.get('allOf',[]):found+=_schema_keywords(sub)
    return found


def validate_subset(schema,document):
    """Validate exact vocabulary of bundled candidate schema; report unhandled keywords."""
    unknown=set(_schema_keywords(schema))-SUPPORTED
    if unknown:return [f'Vérification portable impossible : mots-clés JSON Schema inconnus {sorted(unknown)}']
    errors=[]

    def check(node,value,path,depth=0,probe=False):
        if depth>45:return [f'{path}: structure trop profonde']
        e=[]
        if '$ref' in node:
            ref=node['$ref']
            if not ref.startswith('#/$defs/') or ref.split('/')[-1] not in schema.get('$defs',{}):
                return [f'{path}: référence de schéma non prise en charge']
            e.extend(check(schema['$defs'][ref.split('/')[-1]],value,path,depth+1))
        typ=node.get('type')
        if typ:
            okay={'object':lambda v:isinstance(v,dict), 'array':lambda v:isinstance(v,list),
                  'integer':lambda v:isinstance(v,int) and not isinstance(v,bool),
                  'number':lambda v:isinstance(v,(int,float)) and not isinstance(v,bool),
                  'string':lambda v:isinstance(v,str),'boolean':lambda v:isinstance(v,bool)}.get(typ)
            if okay is None:return [f'{path}: type non pris en charge {typ}']
            if not okay(value):return [f'{path}: type attendu {typ}']
        if 'const' in node and value!=node['const']:e.append(f'{path}: valeur fixe attendue {node["const"]!r}')
        if 'enum' in node and value not in node['enum']:e.append(f'{path}: hors choix autorisés')
        if isinstance(value,str):
            if len(value)<node.get('minLength',0):e.append(f'{path}: texte trop court')
            if 'pattern' in node and re.search(node['pattern'],value) is None:e.append(f'{path}: format de texte invalide')
        if isinstance(value,(float,int)) and not isinstance(value,bool):
            if 'minimum' in node and value<node['minimum']:e.append(f'{path}: sous le minimum')
            if 'maximum' in node and value>node['maximum']:e.append(f'{path}: dépasse le maximum')
        if isinstance(value,dict):
            for required in node.get('required',[]):
                if required not in value:e.append(f'{path}.{required}: champ obligatoire manquant')
            fields=node.get('properties',{})
            if node.get('additionalProperties') is False:
                for key in value:
                    if key not in fields:e.append(f'{path}.{key}: champ non admis')
            for key,desc in fields.items():
                if key in value:e.extend(check(desc,value[key],f'{path}.{key}',depth+1))
        if isinstance(value,list):
            if len(value)<node.get('minItems',0):e.append(f'{path}: trop peu de valeurs')
            if 'items' in node:
                for i,val in enumerate(value):e.extend(check(node['items'],val,f'{path}[{i}]',depth+1))
        for x in node.get('allOf',[]):e.extend(check(x,value,path,depth+1))
        if 'if' in node and not check(node['if'],value,path,depth+1,True):
            if 'then' in node:e.extend(check(node['then'],value,path,depth+1))
        return e

    errors.extend(check(schema,document,'root'))
    return errors
