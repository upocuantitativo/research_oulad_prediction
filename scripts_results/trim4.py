# -*- coding: utf-8 -*-
import re
p=r'C:\Users\Usuario\OneDrive - Universidad Pablo de Olavide de Sevilla\Escritorio\1_ARTÍCULO\1_ARTÍCULO MOTIVACIÓN_Bel_Gol_Has\MANUSCRITO_MPI_OULAD.md'
t=open(p,encoding='utf-8').read()
pairs=[]
def add(o,n): pairs.append((o,n))

add("To test whether higher-capacity architectures change predictive structure or interpretability, we include sequence and tabular deep learners—an LSTM with attention over weekly VLE sequences, and two transformer architectures for tabular data, FT-Transformer (feature tokenisation) and TabTransformer (categorical embeddings)—as well as a hybrid Random Forest enriched with sentence-transformer embeddings of categorical context.",
"To test whether higher-capacity architectures change predictive structure, the pipeline also specifies deep learners—an LSTM with attention over weekly VLE sequences and two tabular transformers (FT-Transformer, TabTransformer)—and a hybrid RF with sentence-transformer embeddings.")

add("The leakage-safe, week-cumulative model answers the timing question concretely: reliable prediction (AUC ≥ 0.90) is first attained at **week 20**, with actionable triage (AUC around 0.87) by week 16. This quantifies, for OULAD, the accuracy-versus-earliness trade-off that prior work described qualitatively (Adnan et al., 2021; Hellas et al., 2018), giving institutions a defensible window in which intervention is both early enough to matter and confident enough to justify.",
"On timing, reliable prediction (AUC ≥ 0.90) is first attained at week 20, with usable triage by week 16 (Section 5.4)—quantifying, for OULAD, the accuracy-versus-earliness trade-off prior work described qualitatively (Adnan et al., 2021; Hellas et al., 2018) and giving institutions a defensible intervention window.")

matched=0
for o,n in pairs:
    if o in t: t=t.replace(o,n,1); matched+=1
    else: print('MISS',repr(o[:60]))
open(p,'w',encoding='utf-8').write(t)
body,_,refs=t.partition('## References')
lines=[l for l in body.splitlines() if not l.strip().startswith('|')]
print('matched',matched,'of',len(pairs))
print('BODY incl tables:',len(re.findall(r'\S+',body)),'| PROSE excl tables:',len(re.findall(r'\S+','\n'.join(lines))))
