"""Verified 1-2 sentence Candidate & Biological Hypothesis summaries for all 52 ExploreALS v1.2 portfolio entries."""
from __future__ import annotations

CANDIDATE_HYPOTHESES: dict[str, str] = {
    "C001": (
        "UNC13A (ENSG00000130477) encodes presynaptic Munc13-1, an essential synaptic vesicle-priming protein required for neurotransmitter release at motor synapses. "
        "Nuclear TDP-43 depletion — potentiated by human ALS GWAS risk alleles rs12608932 and rs12973192 — unmasks a frameshifting intron 20–21 cryptic exon whose steric splice correction restores human cortical/spinal motor neuron synaptic transmission and network synchrony (>30% protein threshold; DOI:10.1038/s41586-026-11256-2) orthogonally to STMN2 and KCNQ2 mis-splicing, anchoring a multiplexed splice-rescue regimen."
    ),
    "C002": (
        "STMN2 (ENSG00000104435) encodes stathmin-2, a dynamic microtubule-regulating phosphoprotein indispensable for motor axon outgrowth, repair, and neuromuscular junction maintenance. "
        "Loss of nuclear TDP-43 triggers premature exon-2a splicing and cryptic polyadenylation that truncates canonical STMN2 across sporadic ALS motor neurons; steric blocking of exon-2a aims to restore full-length axonal stathmin-2."
    ),
    "C003": (
        "Ezogabine (CHEMBL41355) is a first-generation small-molecule opener of neuronal Kv7.2/Kv7.3 (KCNQ2/KCNQ3) potassium channels that hyperpolarizes hyperexcitable motor membranes. "
        "Originally tested to suppress intrinsic cortical and spinal motor neuron hyperexcitability in ALS, it serves strictly as a quantitative human pharmacodynamic benchmark (NCT02450552) for next-generation Kv7 modulators and KCNQ2 splice rescue."
    ),
    "C004": (
        "Ceftriaxone (CHEMBL161) is a beta-lactam cephalosporin antibiotic repurposed from rodent transcriptional screens proposing upregulation of the astrocytic glutamate transporter EAAT2 (SLC1A2). "
        "Its ALS hypothesis proposed that elevating perisynaptic glutamate clearance would prevent excitotoxic motor neuron degeneration."
    ),
    "C005": (
        "Motor neuron excitability in ALS follows a biphasic trajectory: early intrinsic hyperexcitability driven by TDP-43-mediated KCNQ2 loss transitions into late symptomatic synaptic attrition and hypoexcitability. "
        "This companion protocol pairs paradigm-locked threshold-tracking cortical TMS (TT-SICI <=5.5% RMT, PMID:42592079), axonal threshold tracking (SDTC), and CLSI EP09c-bridged living-CSF NPTX2 to stage-gate KCNQ2 interventions prior to synaptic collapse."
    ),
    "C006": (
        "KCNQ2 (ENSG00000075043) encodes the pore-forming Kv7.2 voltage-gated potassium channel subunit that generates the stabilizing M-current in motor neurons. "
        "Nuclear TDP-43 loss induces in-frame exon-5 skipping (PMID:41174170), producing an NMD-escaping, ER-retained dominant-negative subunit (KCNQ2-DeltaE5) that lacks Trp236 and imposes a surface-channel-density ceiling on small-molecule openers; intrathecal steric splice restoration aims to re-establish native Kv7.2 conductance."
    ),
    "C007": (
        "IL1RL1 (ENSG00000115602) encodes two opposing interleukin-33 receptor isoforms: membrane-bound ST2L, which drives protective Treg and microglial signaling, and secreted soluble sST2, an intron-8-polyadenylated decoy receptor. "
        "Motivated by cortical endothelial and cervical MN-niche gene-level IL1RL1 induction, this isoform-unresolved hypothesis tests whether pre-hypoxic ALS neurovasculature secretes excess decoy sST2 and whether selective sST2 suppression (sparing Treg ST2L) restores neuroprotective IL-33 tone."
    ),
    "C008": (
        "Memantine (CHEMBL807) is an uncompetitive, low-affinity NMDA glutamate receptor channel blocker used clinically in Alzheimer disease. "
        "Its ALS repurposing hypothesis proposed that tonic postsynaptic NMDA receptor blockade would attenuate glutamate-mediated Ca2+ influx and excitotoxic motor neuron death."
    ),
    "C009": (
        "Trazodone (CHEMBL621) is a sedating serotonin antagonist/reuptake inhibitor repurposed from phenotypic screens suggesting downstream restoration of eIF2B-mediated translation during chronic integrated stress response (ISR) activation. "
        "Its ALS hypothesis proposed that alleviating persistent eIF2alpha-phosphorylation translational arrest would rescue stressed motor neurons."
    ),
    "C010": (
        "Ropinirole (CHEMBL589) is a dopamine D2/D3 receptor agonist nominated from patient iPSC motor neuron screens proposing both receptor-dependent neurite protection and receptor-independent antioxidant/cholesterol-biosynthetic rescue. "
        "Its hypothesis tested whether chronic oral dosing could slow functional motor decline and neurofilament release in sporadic ALS."
    ),
    "C011": (
        "Furosemide (CHEMBL35) is a systemic loop diuretic and weak sulfamoylbenzoic inhibitor of Na+-K+-2Cl- cotransporters (NKCC1/SLC12A2). "
        "Its repurposing hypothesis proposed blocking chloride import to restore inhibitory GABAergic/glycinergic chloride gradients across hyperexcitable spinal motor circuits."
    ),
    "C012": (
        "Perampanel (CHEMBL1214124) is a brain-penetrant, non-competitive AMPA-type glutamate receptor antagonist clinically used in epilepsy. "
        "Its ALS hypothesis proposed that blocking postsynaptic GluA-mediated fast excitatory transmission (including Ca2+-permeable GluA2-unedited AMPA receptors) would halt excitotoxic motor neuron loss."
    ),
    "C013": (
        "Riluzole (CHEMBL744) is an approved oral benzothiazole ALS standard-of-care agent that preferentially inhibits persistent voltage-gated Na+ current (INaP via NaV1.6/SCN8A) and dampens presynaptic glutamate release. "
        "Within this portfolio, it serves as the foundational clinical survival reference and positive stage-4 human iPSC motor neuron assay benchmark."
    ),
    "C014": (
        "CHMP7 (ENSG00000147457) and CHMP2B (ENSG00000083937) are ESCRT-III nuclear-envelope surveillance factors that remodel damaged nuclear pore complexes. "
        "In sporadic and C9orf72 ALS, aberrant SUN1-facilitated nuclear retention of CHMP7 (modulated by CHMP2B) initiates nucleoporin stripping upstream of nuclear TDP-43 loss; this subunit-resolved hypothesis tests whether selective nuclear-import blockade rescues pore integrity without ablating essential membrane repair."
    ),
    "C015": (
        "SCFD1 (ENSG00000092108) and G2E3 (ENSG00000092140) span the genome-wide significant human ALS chr14q12 GWAS locus, pairing opposing motor-neuron (+0.048) vs primary/iPSC-microglial (-0.22 to -0.33, PP_H4=0.88–0.89) SCFD1 eQTL colocalization with G2E3 exon-2 sQTLs and TDP-43-regulated Intron-1 cryptic polyadenylation. "
        "Because G2E3's Alu-derived cryptic exon fails 0-mismatch transcriptome hybridization safety and SCFD1 is pan-essential, this hypothesis gates bidirectional motor-neuron and microglial secretory effector dissection."
    ),
    "C016": (
        "FBXL5 (ENSG00000118564) is a dual-cofactor iron- and oxygen-sensing SCF E3 ubiquitin ligase subunit (PDB 3V5Z / PDB 6VCD, PMID:32126207) that recruits iron-regulatory protein IRP2 (IREB2) when cytosolic iron is replete. "
        "Because TDP-43 loss induces 3'-UTR lengthening across FBXL5 and IREB2 while postmortem neuronal TFRC/IREB2 are depleted and glial FBXL5 rises, this bidirectional sensor-probe hypothesis resolves functional neuronal iron starvation vs. overload before any lead chemistry."
    ),
    "C017": (
        "CHIT1 (ENSG00000133063), GPNMB (ENSG00000136235), CHI3L1, and CHI3L2 form a coordinated microglial/astroglial chitinase and endolysosomal glycoprotein signature elevated in symptomatic ALS relative to asymptomatic carriers and controls. "
        "Human genetic null homozygosity (CHIT1 rs3831317) and protective lysosomal sign analysis (GPNMB) establish this four-protein suite as a living-CSF symptomatic staging, ALS-Glia stratification, and pharmacodynamic biomarker panel rather than an inhibition target."
    ),
    "C018": (
        "Complement C1q (encoded by microglial C1QA/C1QB/C1QC, ENSG00000173372) initiates classical synaptic pruning and undergoes C3-independent neuronal uptake into ribonucleoprotein complexes. "
        "Distinct from systemic C3/C5 complement blockade, this exploratory hypothesis tests whether CNS-restricted, half-life-extended intrathecal C1q blockade protects vulnerable motor synapses without depleting systemic serum C1q or protective spinal C-boutons."
    ),
    "C019": (
        "Baricitinib (CHEMBL2105759) is an oral ATP-competitive JAK1/JAK2 tyrosine kinase inhibitor that suppresses cytokine-induced STAT phosphorylation. "
        "The dual ALS hypothesis proposes dampening gp130/OSMR–JAK1–STAT3 neuroinflammation in biomarker-defined ALS-Glia patients (while probing autonomous TDP-43-linked neuronal JAK2 3'-UTR shortening), gated on selective JAK1 vs. JAK2 exposure and thrombotic safety."
    ),
    "C020": (
        "Apilimod (CHEMBL4297643; clinical dimesylate salt AIT-101) is a potent lipid kinase inhibitor of endolysosomal PIKfyve (ENSG00000115020), which synthesizes PI(3,5)P2 to regulate autophagosome-lysosome fusion and unconventional secretory clearance. "
        "Because continuous QD/BID PIKfyve inhibition triggers neuronal ClC-7 vacuolation, +PI(3)P–LRRK2/CASM stress, and clinical NfL/GFAP surges despite lowering C9orf72 CSF poly(GP), this hypothesis tests whether intermittent pulsed dosing can uncouple net intracellular clearance from vacuolar toxicity."
    ),
    "C021": (
        "Icerguastat (Sephin1, CHEMBL2365743) is a chlorobenzylidene aminoguanidine small molecule originally proposed to prolong protective eIF2alpha phosphorylation by selectively inhibiting the stress-inducible phosphatase cofactor PPP1R15A (GADD34). "
        "Its ALS hypothesis tested whether oral dosing could attenuate endoplasmic reticulum proteotoxic stress and slow bulbar/limb progression."
    ),
    "C022": (
        "DNAJB2 (ENSG00000135924, HSJ1) encodes a neuronal Hsp40 co-chaperone with two alternatively spliced isoforms: cytosolic DNAJB2a (ENST00000392086), which clears misfolded ubiquitylated TDP-43, and intron-9-retaining ER-prenylated DNAJB2b, with recessive human loss-of-function mutations (OMIM 614881) causing distal motor neuropathy and juvenile ALS. "
        "Backed by concordant human cortical oligodendrocyte, cervical spinal cord, and synaptosomal protein loss, this hypothesis benchmarks AAV-DNAJB2a cDNA augmentation against internal intron-9 ISS/IPA competition (chr2:219284988-219285939(+), sparing the 3' splice site and mature DNAJB2b ERAD)."
    ),
    "C023": (
        "YKT6 (ENSG00000106636) encodes an autoinhibited Longin R-SNARE required for ER-to-Golgi and autophagosome membrane fusion that harbors an exome-wide rare human ALS missense risk variant (p.Tyr64Cys, rs138273846, PMID:41917433) inside its Longin groove (modeled in rat DPC-bound PDB 3KYQ, PMID:20159557) alongside TDP-43 3'-UTR lengthening and PTAR1 Exon-2 skipping. "
        "Because YKT6 and partner cis-Golgi SNAREs (STX5, NSF) are cellularly pan-essential, this hypothesis tests positive allele-split Longin-groove or exosite stabilization without ejecting endogenous Cys195-farnesyl."
    ),
    "C024": (
        "Pegcetacoplan is a subcutaneously administered ~43.5 kDa PEGylated cyclic peptide inhibitor of central complement component C3 (ENSG00000125730) that blocks classical, lectin, and alternative C3 convertase cleavage. "
        "Evaluated clinically in the 249-patient Phase 2 MERIDIAN trial (NCT04579666), its ALS hypothesis proposed that systemic C3 inhibition would halt complement-mediated motor axon and neuromuscular junction injury."
    ),
    "S01": (
        "Dexmedetomidine (CHEMBL778) is a potent intravenous alpha-2A adrenergic receptor agonist clinically restricted to intensive-care sedation and anesthesia. "
        "Nominated after rescuing sporadic ALS patient iPSC motor neurons at 2.5 uM in vitro, its repurposing hypothesis proposed neuroprotective adrenergic or imidazoline signaling."
    ),
    "S02": (
        "CuATSM (CHEMBL4297372) is a brain-penetrant copper(II) bis(thiosemicarbazone) complex proposed to deliver bioavailable copper to metal-deficient superoxide dismutase and scavenge peroxynitrite radicals. "
        "Survival rescue in mutant SOD1 rodent models and 2.5 uM human sALS iPSC motor neuron screens motivated testing oral CuATSM in sporadic ALS."
    ),
    "S03": (
        "Mycophenolate mofetil (CHEMBL1456, prodrug of mycophenolic acid CHEMBL866) is a reversible inhibitor of inosine monophosphate dehydrogenase (IMPDH) that blocks de novo guanosine nucleotide synthesis in proliferating lymphocytes. "
        "Nominated from 2.5 uM iPSC motor neuron survival screens and peripheral neuroimmune hypotheses, it was proposed to suppress adaptive immune-mediated motor neuron injury."
    ),
    "S04": (
        "Tamoxifen (CHEMBL83) is a lipophilic selective estrogen receptor modulator that also inhibits protein kinase C and induces autophagic flux at micromolar concentrations in vitro. "
        "Nominated from sporadic ALS iPSC motor neuron survival screens and historical clinical observations, its repurposing hypothesis proposed neuroprotective autophagy or PKC modulation."
    ),
    "S05": (
        "Lonafarnib (CHEMBL298734) and Tipifarnib (CHEMBL289228) are potent small-molecule inhibitors of protein farnesyltransferase (FTase) developed in oncology and progeria. "
        "Their repurposing hypothesis proposed blocking C-terminal CAAX farnesylation to enhance autophagic protein clearance in neurodegenerative proteinopathies."
    ),
    "S06": (
        "SARM1 (ENSG00000004139) encodes the central NAD+-cleaving TIR-domain executioner enzyme of Wallerian axon degeneration, activated post-translationally when distal axonal NMNAT2 depletion raises the NMN/NAD+ ratio and unlocks its autoinhibitory ARM domain. "
        "Backed by rare human ALS gain-of-function variants and low heterozygous pLoF constraint in gnomAD v4, S06 tests oral allosteric ARM–TIR octamer T-lock inhibitors (benchmarked on PDB 7DJT) to silence motor axonolysis without the sub-inhibitory filament activation seen with orthosteric base-exchange prodrugs (PDB 9TZY)."
    ),
    "S07": (
        "Aldesleukin (CHEMBL1201438) is recombinant human interleukin-2 administered subcutaneously at low doses to selectively expand immunosuppressive CD4+CD25+FOXP3+ regulatory T cells (Tregs) via high-affinity IL2RA receptors without activating effector T cells. "
        "Following the MIROCALS Phase 2b trial (NCT03039673, PMID:40354799) — which missed unadjusted overall survival (p=0.33) but showed positive SAP-prespecified covariate-adjusted survival (HR=0.32, p=0.007) and a 48% mortality hazard reduction in the 750–3,700 pg/mL BioVendor ELISA CSF pNfH stratum — S07 tests prospective calibrated biomarker-gated Treg immunomodulation."
    ),
    "S08": (
        "Methylcobalamin (CHEMBL4297672) is the active coenzyme form of vitamin B12 required by methionine synthase to remethylate neurotoxic homocysteine and sustain neuronal transmethylation. "
        "Validated in the early-window (<=12m onset) Phase 3 JETALS trial (NCT03548311, N=129 FAS, PMID:35532908) and approved broadly for ALS functional slowing in Japan on Sept 24, 2024 (Rozebalamin 50 mg IM 2x/wk), it serves as a regional standard-of-care benchmark whose negative live-imaging screen readout highlights plausible Co-C photolysis risk."
    ),
    "S09": (
        "Censavudine (TPN-101, CHEMBL124363) is an oral nucleoside reverse transcriptase inhibitor of endogenous LINE-1 retrotransposons, which become derepressed upon nuclear TDP-43 loss in the ~13.4–13.5% cortical ALS-TE molecular subtype. "
        "Selected in May 2025 for the Phase 2/3 HEALEY ALS Platform Trial following mixed C9orf72-ALS/FTD Phase 2a biomarker and vital-capacity signals (NCT04993755), this hypothesis tests living-CSF ORF1p/L1HS biomarker-stratified LINE-1 RT inhibition and post-mitotic neuronal triphosphorylation in sporadic ALS-TE."
    ),
    "DN-01": (
        "ATG4B (ENSG00000168397) encodes the primary mammalian cysteine protease (PDB 2Z0D) that primes pro-LC3B and recycles lipidated LC3-II to sustain neuronal autophagosome biogenesis. "
        "Nuclear TDP-43 depletion unmasks a frame-truncating cryptic exon after Val319 that deletes the C-terminal LC3-interacting region and depletes CNS ATG4B protein; intrathecal steric splice-switching aims to restore autophagic proteostasis in motor neurons."
    ),
    "DN-02": (
        "KALRN (ENSG00000160145) encodes Kalirin, a dual-RhoGEF synaptic scaffold whose full-length Kalirin-12/DuET isoforms carry a C-terminal serine/threonine kinase domain regulating dendritic spine stability. "
        "TDP-43 loss induces MANE Select KALRN-226 intron-53 cryptic-exon inclusion across C9orf72-FTD/ALS cortex (with published cortical iNeuron 2'-MOE/PS ASO and FTD-MND BaseScope validation, PMID:42234776) that truncates the C-terminal kinase while sparing Kalirin-7; steric splice blockade tests whether adult spinal motor-neuron penetrance supports motor rescue."
    ),
    "DN-03": (
        "PTPRT (ENSG00000196090) encodes a CNS-restricted receptor protein tyrosine phosphatase that stabilizes trans-synaptic Neuroligin/Fyn adhesion complexes (PMID:19816407) while dephosphorylating STAT3 Tyr705 (PMID:17360477). "
        "Multi-cohort screening revealed severe Ribo-seq and C9-FTD cortical homogenate protein depletion (alongside null synaptosomal DIA and FDR-non-significant CSF ectodomain trends); this hypothesis tests fine-mapping its 3.57-kb Intron-26 cryptic junction and resolving synaptic adhesion vs. neurotrophic pSTAT3 polarity."
    ),
    "DN-04": (
        "CELF5 (ENSG00000161082) encodes a brain- and motor-system-restricted CUGBP Elav-like RNA-binding factor that regulates neuron-specific alternative splicing. "
        "Depletion of nuclear TDP-43 induces inclusion of a 108-bp nonsense-mediated-decay cryptic exon (replicated at LeafCutter cluster clu_25763_+ in sporadic ALS patient iPSC motor neurons); intrathecal steric splice-switching aims to prevent secondary RNA-processing collapse downstream of TDP-43 loss."
    ),
    "DN-05": (
        "PRUNE2 (ENSG00000106772) encodes a large BNIP2-homology neuronal protein whose C-terminal BCH domain is homologous to RhoA-inhibiting BNIP2-XL in cell-line models (PMID:18445682). "
        "Identified as the sole TDP-43 cryptic-splicing candidate significantly depleted across 55-um human ALS cervical anterior-horn MN-niche Visium spots alongside C9-FTD synaptosomal protein loss, this hypothesis tests resolving and sterically rescuing its Exon 11–12 mis-spliced junction."
    ),
    "DN-06": (
        "PFKP (ENSG00000067057) encodes the platelet isoform of phosphofructokinase-1, a glycolytic gatekeeper partitioning neuronal glucose between ATP generation and the antioxidant pentose phosphate pathway (PPP, PMID:19448625). "
        "Because its TDP-43-regulated exon is an endogenous GENCODE NMD poison exon (ENSE00004576209) with >10% inclusion in control human motor cortex and spinal cord (PMID:41332610), steric blockade tests whether rescuing synaptic PFKP aids bioenergetics without bystander PPP NADPH/glutathione depletion."
    ),
    "DN-07": (
        "TRAPPC12 (ENSG00000171853) encodes an outer subunit of the TRAPPIII tethering complex involved in ER-to-Golgi transport and autophagosome assembly (recessive PEBAS OMIM 617669) upstream of YKT6. "
        "Nuclear TDP-43 depletion increases usage of a GENCODE-annotated, non-selective intronic alternative last exon (82.9% TDP+ vs. 34.0% non-TDP baseline, PMID:41120751) that truncates TRAPPC12 translation; steric 3'-splice-site blockade tests restoring full-length trafficking."
    ),
    "DN-08": (
        "ELK1 (ENSG00000126767, non-PAR Xp11.23) encodes an ERK-responsive ETS transcription factor with compartment-dependent polarity: nuclear SRF co-activation supports neuronal survival, whereas dendritic ELK1 translation promotes apoptosis. "
        "TDP-43 loss derepresses a 3.90-kb terminal 3'-UTR extension that increases neuronal ELK1 protein (PMID:41120751); this exploratory hypothesis benchmarks 3'-extension-selective RNase-H gapmer window #1 against steric distal-PAS blockade and cytoplasmic 3'-extension siRNA (with mandatory Exon 1–6 counter-screens) to resolve polarity."
    ),
    "DN-09": (
        "DLGAP1 (ENSG00000170579, GKAP) encodes a core postsynaptic density scaffold linking glutamate receptor-associated PSD-95 complexes to Shank cytoskeleton assemblies. "
        "TDP-43 cryptic-polyadenylation discovery identified a pathology-selective 5'-UTR Intron-2 alternative last exon (17/926 TDP+ vs. 0/750 non-TDP NYGC libraries, PMID:41120751) paired with cortical homogenate and synaptosomal DLGAP1 loss; steric 3'-splice-site blockade tests rescuing distal-promoter scaffold expression."
    ),
    "DN-10": (
        "DPP6 (ENSG00000130226) encodes a catalytically inactive S9B dipeptidyl-peptidase homolog (PDB 1XFD 3.00A homodimer: Ser->Asp712 in GKDYGG, PMID:15476821) that assembles with somatodendritic Kv4.2 A-type potassium channels to regulate dendritic excitability. "
        "Identified as the top downregulated untargeted protein in Emory ALS CSF DIA proteomics alongside cortical synaptosome depletion (with MS2-TMTpro omnibus discordance pending PRM bridging), it serves as a pre-validation candidate fluid marker of somatodendritic attrition."
    ),
    "DN-11": (
        "DPP10 (ENSG00000175497) encodes a catalytically inactive neuronal Kv4 potassium-channel auxiliary subunit paralogous to DPP6 (UniProt Q8N608: Ser->Gly651 in GKGYGG; LOEUF=0.378) that governs somatodendritic A-type current gating. "
        "Co-depleted with DPP6 in Emory ALS CSF DIA proteomics and primary motor cortex excitatory neurons (with MS2-TMTpro omnibus and WashU non-parametric caveats), it serves as a pre-validation candidate fluid marker of somatodendritic attrition."
    ),
    "DN-12": (
        "CFL1 (ENSG00000172757) encodes cofilin-1, a pan-essential actin-severing protein whose LIMK1-driven Ser3 hyperphosphorylation (inactivation) triggers TDP-43 aggregation in sporadic ALS spinal motor neurons (Jagaraj et al. 2026, PMID:41804798 — opposite in phospho-polarity to dephospho-cofilin rods). "
        "Consistently elevated as unmodified pan-CFL1 across living ALS CSF DIA and TMTpro cohorts (surviving erythrocyte/platelet lysis OLS controls) while cellularly pan-essential, CFL1 serves as a pre-validation candidate fluid cytoskeletal injury marker requiring pSer3-vs-total isoform assay bridging."
    ),
    "DN-13": (
        "MAOB (ENSG00000069535) encodes outer-mitochondrial-membrane monoamine oxidase B, an H2O2-generating flavoprotein predominantly expressed in astrocytes. "
        "Nominated from postmortem spinal spatial transcriptomic and cortical homogenate increases, its therapeutic hypothesis proposed irreversible MAO-B inhibition (rasagiline/selegiline class, NCT01879241) to curb glial oxidative stress in ALS."
    ),
    "DN-14": (
        "PMX 205 (ALS-205, PubChem CID:6918845; completed subcutaneous Phase 1a/1b ACTRN12622000927729) is a cyclic hexapeptide orthosteric intrahelical Site-2 antagonist of the complement C5a receptor C5aR1 (ENSG00000197405; analog PMX-53 resolved in PDB 6C1R, PMID:29867214, distinct from extrahelical allosteric avacopan CHEMBL3989871). "
        "Identified as a sub-FDR survival candidate (#9/107, q=0.070 in C5/C5a-free monocultures) without a completed human C5aR1 ALS efficacy trial, this exploratory hypothesis tests whether selective C5aR1 blockade acts on-target in MN-microglia co-cultures despite negative upstream C5/C3 ALS trials (PMID:39960672)."
    ),
    "DN-15": (
        "Lamotrigine is an oral phenyltriazine voltage-gated Na+ channel blocker that stabilizes presynaptic membranes and inhibits pathological glutamate release. "
        "Resurfacing as a nominal survival hit in sporadic ALS iPSC motor neuron screening, its repurposing hypothesis proposed attenuating glutamatergic motor hyperexcitability in human ALS (PMID:7906190, PMID:12807386)."
    ),
    "DN-16": (
        "Dolutegravir is an HIV-1 integrase strand-transfer inhibitor evaluated clinically within fixed-dose Triumeq (alongside abacavir/lamivudine, NCT05193994) to suppress endogenous retroviral HERV-K expression implicated in TDP-43 pathology. "
        "Nominated from nominal in vitro iPSC motor neuron survival screening, its hypothesis proposed antiretroviral suppression of retroelement neurotoxicity in unstratified ALS."
    ),
    "DN-17": (
        "Acetylcysteine (N-acetylcysteine) is a thiol-donor prodrug of intracellular glutathione and a scavenger of reactive oxygen species that reaches micromolar human CSF levels at high doses (70 mg/kg oral BID, PMID:25765302). "
        "Following an underpowered 50 mg/kg/d subcutaneous ALS survival trial (HR=0.74 [0.41–1.33], PMID:7763202) and sub-FDR 2.5 uM iPSC motor neuron survival screening, this exploratory hypothesis tests whether high-dose CNS-penetrant NAC restores neuronal glutathione beyond extracellular media thiol buffering."
    ),
    "DN-18": (
        "Coenzyme Q10 (ubiquinone) is an inner-mitochondrial-membrane electron carrier between Complexes I/II and Complex III that also acts as a lipid-soluble antioxidant. "
        "Nominated from marginal survival extension in sporadic ALS iPSC motor neuron screening, its hypothesis proposed high-dose oral supplementation to rescue motor neuron bioenergetics and lipid peroxidation (NCT00243932, PMID:19743457)."
    ),
    "DN-19": (
        "L-Serine is an obligate substrate of serine palmitoyltransferase proposed to competitively suppress neurotoxic 1-deoxysphingolipids in sporadic ALS, while strictly contraindicated in <0.5% monogenic SPTLC1/SPTLC2 gain-of-function ALS where ORMDL feedback loss drives canonical C18–C22 ceramide overproduction (PMID:34059824; PMID:43025655). "
        "Because fixed 2.5 uM library screening adds only +0.625% atop ~400 uM basal media L-serine and zero randomized placebo-controlled sporadic ALS trials have completed (NCT01835782; NCT03580616), this exploratory hypothesis tests physiological low-serine dose-response and genetically gated systemic supplementation."
    ),
}
