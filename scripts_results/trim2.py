# -*- coding: utf-8 -*-
import re
p=r'C:\Users\Usuario\OneDrive - Universidad Pablo de Olavide de Sevilla\Escritorio\1_ARTÍCULO\1_ARTÍCULO MOTIVACIÓN_Bel_Gol_Has\MANUSCRITO_MPI_OULAD.md'
t=open(p,encoding='utf-8').read()
pairs=[]
def add(o,n): pairs.append((o,n))

# Intro p2: remove disparity numbers duplicated in 5.1
add("In other words, 52.8% of enrolments result in a negative outcome. These figures mask sharp disparities. Withdrawal reaches 37.2% in the most deprived Index of Multiple Deprivation (IMD) areas versus 25.9% in the least deprived; students declaring a disability withdraw at 39.4% versus 30.3%; and attainment is stratified by prior education, with postgraduate entrants achieving Distinction at 28.1% against only 4.6% for entrants with no formal qualifications. Such gradients show that failure online tracks structural vulnerability, making early-warning design simultaneously a predictive and a fairness problem.",
"In other words, 52.8% of enrolments result in a negative outcome, and these figures mask sharp disparities by deprivation, disability, and prior education (quantified in Section 5.1). Such gradients show that failure online tracks structural vulnerability, making early-warning design simultaneously a predictive and a fairness problem.")

# Intro p4 gap tighten
add("Some of this work does aggregate behaviour into composites—engagement and activity indices that rank highly as predictors (Hussain et al., 2018; Wolff et al., 2013)—and the broader LMS literature offers composites of regularity and procrastination that correlate with achievement (You, 2016; Saqr et al., 2017). But these composites are assembled for predictive yield, not derived from a motivational theory, validated dimension by dimension against it, and reported when individual dimensions fail. In parallel, fairness and explainability have advanced as largely separate concerns, each studied apart from the other and rarely on OULAD.",
"Some of this work aggregates behaviour into composites that rank highly as predictors (Hussain et al., 2018; Wolff et al., 2013; You, 2016; Saqr et al., 2017), but these are assembled for predictive yield—not derived from a motivational theory, validated dimension by dimension, and reported when dimensions fail. Fairness and explainability, meanwhile, have advanced as separate concerns, each rarely on OULAD.")

# Intro contributions: fourth
add("Fourth, it advances fairness-aware modelling, applying formal bias metrics—demographic parity and equalised odds—to audit outcomes for students with declared disabilities and those with a history of prior failure, groups for whom fairness in at-risk prediction has been flagged as a pressing concern (RQ3; Hutt et al., 2019; Riazy et al., 2020).",
"Fourth, it applies formal bias metrics—demographic parity and equalised odds—to audit outcomes for students with disabilities and prior failure, with group-aware mitigation (RQ3; Hutt et al., 2019; Riazy et al., 2020).")

# 2 predicting tail
add("Ouyang et al. (2022) combined learning-process and behavioural data to improve performance prediction, while Hlosta et al. (2017) proposed the \"Ouroboros\" approach to identify at-risk students early without relying on labelled legacy data. A recurring concern across this literature is timing: Adnan et al. (2021) showed that predictive accuracy rises as a course progresses and explicitly modelled at-risk identification at different percentages of course length for early intervention, a finding echoed in systematic reviews of academic-performance prediction (Hellas et al., 2018).",
"Ouyang et al. (2022) combined learning-process and behavioural data, and Hlosta et al. (2017) identified at-risk students early without labelled legacy data. On timing, Adnan et al. (2021) showed predictive accuracy rises with course length, modelling at-risk identification at different course percentages—echoed in systematic reviews (Hellas et al., 2018).")

# 2 fairness tighten
add("Hutt et al. (2019) demonstrated that models predicting student outcomes can be both unfair and poorly generalisable across demographic groups, and recommended that demographic attributes be used primarily for bias auditing rather than as primary decision drivers. Riazy et al. (2020) examined fairness specifically in at-risk prediction within virtual learning environments, showing that disparities in error rates can disadvantage already vulnerable subgroups.",
"Hutt et al. (2019) showed that outcome-prediction models can be unfair and poorly generalisable across groups, recommending demographic attributes for auditing rather than decision-making. Riazy et al. (2020) showed that error-rate disparities in at-risk prediction can disadvantage vulnerable subgroups.")

# 2 explainable tighten
add("**Explainable AI in educational prediction.** Interpretability has emerged as a precondition for educator trust and pedagogical usefulness. Beyond the feature-importance analyses pioneered for OULAD (Hussain et al., 2018), explainability is increasingly used to make week-wise and course-level predictions transparent to practitioners, supporting the identification of students in need of attention and the explanation of why a learner is flagged. This positions explainable analytics not as a post hoc accessory but as integral to actionable early-warning design. A largely unresolved question is whether the interpretability of simpler models is retained when higher-capacity deep and transformer architectures are introduced, and whether the two model families agree on which behaviours matter, an issue our comparative SHAP analysis (RQ1) addresses directly.",
"**Explainable AI in educational prediction.** Interpretability is a precondition for educator trust. Beyond feature-importance analyses for OULAD (Hussain et al., 2018), explainability increasingly makes week-wise predictions transparent, explaining why a learner is flagged—integral to, not a post hoc accessory of, early-warning design. Whether the interpretability of simple models survives in higher-capacity deep and transformer architectures remains open; our SHAP analysis addresses the classical side (RQ1).")

# 3.1 last sentence
add("This autonomy-intensive character explains why two learners of comparable prior attainment can diverge sharply: heightened self-direction amplifies the behavioural consequences of motivational differences, making motivation a powerful—yet, in most administrative datasets, unmeasured—lever for early prediction.",
"This autonomy-intensive character makes motivation a powerful—yet usually unmeasured—lever for early prediction: heightened self-direction amplifies the behavioural consequences of motivational differences.")

# 3.2 meta-analysis tighten
add("A large meta-analysis from the SDT tradition confirms that autonomous motivation is robustly associated with positive academic outcomes, including persistence and achievement, whereas controlled motivation is weakly or negatively related to them (Howard et al., 2021), and that these motivational orientations themselves arise from identifiable need-supportive antecedents (Bureau et al., 2022).",
"Meta-analytic evidence confirms that autonomous motivation is robustly associated with persistence and achievement, controlled motivation weakly or negatively, and that these orientations arise from need-supportive antecedents (Howard et al., 2021; Bureau et al., 2022).")

# 3.5 engagement tail
add("Consistent and persistent engagement patterns have repeatedly predicted achievement and retention in LMS settings (Macfadyen & Dawson, 2010; You, 2016; Saqr et al., 2017), and trajectory analyses show that stable engagement over time, not isolated bursts, distinguishes successful learners (Saqr & López-Pernas, 2021).",
"Consistent engagement predicts achievement and retention in LMS settings (Macfadyen & Dawson, 2010; You, 2016; Saqr et al., 2017), and stable trajectories, not isolated bursts, distinguish successful learners (Saqr & López-Pernas, 2021).")

# 3.5 diversity tail
add("Empirically, the variety and richness of clickstream behaviour has been linked to completion and performance across massive open online course (MOOC) and VLE contexts (Wolff et al., 2013; Crossley et al., 2016), and feature-importance and review studies confirm that activity-type indicators carry predictive weight for academic outcomes (Hellas et al., 2018; Hussain et al., 2018).",
"Empirically, clickstream variety has been linked to completion across massive open online course (MOOC) and VLE contexts (Wolff et al., 2013; Crossley et al., 2016), with activity-type indicators carrying predictive weight (Hellas et al., 2018; Hussain et al., 2018).")

# 6.1 p1 tighten
add("Within the MPI, *engagement consistency* is the strongest signal (r = +0.417 with success); in the leakage-safe model the engagement construct is the single top driver, entering through the proportion of active weeks while the standardised composite proves redundant with it. This directly supports the SDT/SRL premise that regular, planful effort is the behavioural signature of competent self-regulation (Pintrich, 2004; Zimmerman, 2000), echoing trajectory-based engagement research (Saqr & López-Pernas, 2021; You, 2016). *Assessment timeliness* behaves as EVT and the procrastination literature predict (Steel, 2007; Tuckman, 2005), separating successful from unsuccessful learners in the expected direction.",
"Within the MPI, *engagement consistency* is the strongest signal (r = +0.417): in the leakage-safe model the engagement construct is the top driver (via the proportion of active weeks), supporting the SDT/SRL premise that regular, planful effort is the signature of competent self-regulation (Pintrich, 2004; Zimmerman, 2000; Saqr & López-Pernas, 2021). *Assessment timeliness* behaves as EVT and the procrastination literature predict (Steel, 2007; Tuckman, 2005).")

# 6.1 p2 tail tighten
add("Persistence, in turn, was defined for only the 17.4% of students with a sub-40 score and over a coarse 14-day window; its null result suggests that academic buoyancy (Martin & Marsh, 2008; Cassidy, 2016) needs finer temporal operationalisation than a single post-setback ratio. These results caution against assuming that any behaviourally plausible proxy will validate, and they specify exactly which MPI components to re-weight or re-specify—a more useful outcome than an undifferentiated claim that the index works.",
"Persistence was defined for only the 17.4% of students with a sub-40 score, over a coarse 14-day window; its null result suggests academic buoyancy (Martin & Marsh, 2008; Cassidy, 2016) needs finer temporal operationalisation. These results specify which MPI components to re-specify rather than assuming any plausible proxy validates.")

# 7 p1 opener
add("This study set out to make early prediction of academic failure in online higher education theory-grounded, explainable, equitable, and temporally actionable, organised around a Motivation Proxy Index derived from VLE behaviour. Four conclusions follow from the OULAD evidence, in the order of the research questions.",
"We set out to make early prediction of academic failure theory-grounded, explainable, equitable, and temporally actionable, organised around an MPI derived from VLE behaviour. Four conclusions follow, by research question.")

# abstract tail
add("The MPI offers a transferable, interpretable, and equity-conscious foundation for early-warning systems in online education, and we report which proxy operationalisations require re-specification.",
"The MPI offers a transferable, interpretable, equity-conscious foundation for early-warning systems, and we report which proxy operationalisations require re-specification.")

matched=0; missed=[]
for o,n in pairs:
    if o in t:
        t=t.replace(o,n,1); matched+=1
    else:
        missed.append(o[:70])
open(p,'w',encoding='utf-8').write(t)
body,_,refs=t.partition('## References')
lines=[l for l in body.splitlines() if not l.strip().startswith('|')]
print('matched',matched,'of',len(pairs))
for m in missed: print('  MISS',repr(m))
print('BODY incl tables (excl refs):',len(re.findall(r'\S+',body)))
print('PROSE excl table rows:',len(re.findall(r'\S+','\n'.join(lines))))
