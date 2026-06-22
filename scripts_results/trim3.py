# -*- coding: utf-8 -*-
import re
p=r'C:\Users\Usuario\OneDrive - Universidad Pablo de Olavide de Sevilla\Escritorio\1_ARTÍCULO\1_ARTÍCULO MOTIVACIÓN_Bel_Gol_Has\MANUSCRITO_MPI_OULAD.md'
t=open(p,encoding='utf-8').read()
pairs=[]
def add(o,n): pairs.append((o,n))

add("Sections 5.2–5.6 test each proposition directly, and Section 5.8 reports the verdicts—including the dimensions that fail their predicted direction, which we treat as substantive findings rather than as nuisances.",
"Sections 5.2–5.6 test these propositions; Section 5.8 reports the verdicts, including the dimensions that fail.")

add("Testing the framework's propositions directly against the evidence yields a deliberately mixed picture (Table 7), which we regard as the study's theory-testing contribution: it specifies which behavioural operationalisations of motivation validate on OULAD and which do not.",
"Testing the propositions against the evidence yields a deliberately mixed picture (Table 7)—the study's theory-testing contribution: it specifies which behavioural operationalisations of motivation validate on OULAD and which do not.")

add("This matches calls for equity-focused, theory-informed dashboards over opaque accuracy-maximising classifiers (Jovanović et al., 2017; Henrie et al., 2015), reframing the MPI as an explanatory instrument that complements rather than competes with high-capacity predictors.",
"This matches calls for equity-focused, theory-informed dashboards (Jovanović et al., 2017; Henrie et al., 2015), reframing the MPI as an explanatory instrument that complements high-capacity predictors.")

add("The outcome distribution is imbalanced: Pass 37.93% (12,361), Withdrawn 31.16% (10,156), Fail 21.64% (7,052), and Distinction 9.28% (3,024); the combined adverse-outcome (fail or withdraw) rate is 52.8%.",
"The outcome distribution is imbalanced (Pass 37.9%, Withdrawn 31.2%, Fail 21.6%, Distinction 9.3%; combined adverse rate 52.8%).")

matched=0; missed=[]
for o,n in pairs:
    if o in t: t=t.replace(o,n,1); matched+=1
    else: missed.append(o[:60])
open(p,'w',encoding='utf-8').write(t)
body,_,refs=t.partition('## References')
lines=[l for l in body.splitlines() if not l.strip().startswith('|')]
print('matched',matched,'of',len(pairs))
for m in missed: print('  MISS',repr(m))
print('BODY incl tables:',len(re.findall(r'\S+',body)),'| PROSE excl tables:',len(re.findall(r'\S+','\n'.join(lines))))
