"""Verified 1-2 sentence Candidate & Biological Hypothesis summaries for all 59 CarbonALS portfolio entries."""
from __future__ import annotations

CANDIDATE_HYPOTHESES: dict[str, str] = {
    "C001": (
        "UNC13A (ENSG00000130477) encodes presynaptic Munc13-1, an essential synaptic vesicle-priming protein required for neurotransmitter release at motor synapses. "
        "Nuclear TDP-43 depletion — potentiated by human ALS GWAS risk alleles rs12608932 and rs12973192 — unmasks a frameshifting intron 20–21 cryptic exon that degrades UNC13A mRNA via nonsense-mediated decay; intrathecal steric splice-switching aims to restore synaptic Munc13-1 within a multiplexed splice-rescue regimen."
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
        "Rather than bundling disparate ion-channel drugs, this companion protocol pairs transcranial magnetic stimulation (SICI), axonal threshold tracking (SDTC), and living-CSF synaptic markers (NPTX2) to stage-gate KCNQ2 interventions prior to synaptic collapse."
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
        "In sporadic and C9orf72 ALS, aberrant SUN1-facilitated nuclear retention of CHMP7 (modulated by CHMP2B) initiates nucleoporin stripping upstream of nuclear TDP-43 loss; the unbundled hypothesis tests whether selective nuclear-import blockade rescues pore integrity without ablating essential membrane repair."
    ),
    "C015": (
        "Originally bundled as an eight-gene ER-to-Golgi SNARE/vesicle-recycling axis, single-gene dissection isolates two distinct human ALS hypotheses: conformational stabilization of the autoinhibited Longin SNARE YKT6 (ENSG00000106636, harboring rare ALS risk variant p.Tyr64Cys on PDB 3KYQ and TDP-43-impaired PTAR1 prenylation) and cis-regulatory dissection of the colocalized chr14q12 ALS GWAS locus spanning SCFD1 and TDP-43-cryptic G2E3."
    ),
    "C016": (
        "FBXL5 (ENSG00000118564) is an iron- and oxygen-sensing SCF E3 ubiquitin ligase subunit (PDB 6VCD) that degrades iron-regulatory protein IRP2 (IREB2) when cytosolic iron is replete. "
        "Because TDP-43 loss induces 3'-UTR lengthening across FBXL5 and iron-homeostasis transcripts, this exploratory hypothesis asks whether neuron-selective IRP2/iron-axis modulation can prevent ferroptotic stress without stripping glial ferritin reserves via bulk iron chelation."
    ),
    "C017": (
        "CHIT1 (ENSG00000133063), GPNMB (ENSG00000136235), CHI3L1, and CHI3L2 form a coordinated microglial/astroglial chitinase and endolysosomal glycoprotein signature elevated in symptomatic ALS relative to asymptomatic carriers and controls. "
        "Originally evaluated as candidate neuroinflammatory inhibitor targets, human genetic and functional sign analysis reclassifies this four-protein suite as a living-CSF symptomatic staging, ALS-Glia stratification, and lysosomal pharmacodynamic biomarker panel."
    ),
    "C018": (
        "Complement C1q (encoded by microglial C1QA/C1QB/C1QC, ENSG00000173372) initiates classical synaptic pruning and undergoes C3-independent neuronal uptake into ribonucleoprotein complexes. "
        "While systemic C3/C5 complement blockade is clinically falsified in ALS, this unbundled exploratory hypothesis tests whether CNS-restricted, half-life-extended intrathecal C1q blockade protects vulnerable motor synapses without depleting systemic serum C1q or protective spinal C-boutons."
    ),
    "C019": (
        "Baricitinib (CHEMBL2105759) is an oral ATP-competitive JAK1/JAK2 tyrosine kinase inhibitor that suppresses cytokine-induced STAT phosphorylation. "
        "The dual ALS hypothesis proposes dampening gp130/OSMR–JAK1–STAT3 neuroinflammation in biomarker-defined ALS-Glia patients (while probing autonomous TDP-43-linked neuronal JAK2 3'-UTR shortening), gated on selective JAK1 vs. JAK2 exposure and thrombotic safety."
    ),
    "C020": (
        "Apilimod (CHEMBL1200798) is a potent lipid kinase inhibitor of endolysosomal PIKfyve (ENSG00000115020), which synthesizes PI(3,5)P2 to regulate autophagosome-lysosome fusion and unconventional secretory clearance. "
        "Because continuous BID PIKfyve inhibition triggers neuronal ClC-7 vacuolation and clinical NfL/GFAP surges despite lowering C9orf72 CSF poly(GP), this hypothesis tests whether intermittent pulsed dosing can uncouple proteotoxic clearance from vacuolar toxicity."
    ),
    "C021": (
        "Icerguastat (Sephin1, CHEMBL2365743) is a chlorobenzylidene aminoguanidine small molecule originally proposed to prolong protective eIF2alpha phosphorylation by selectively inhibiting the stress-inducible phosphatase cofactor PPP1R15A (GADD34). "
        "Its ALS hypothesis tested whether oral dosing could attenuate endoplasmic reticulum proteotoxic stress and slow bulbar/limb progression."
    ),
    "BA9-01": (
        "AGAP2 (ENSG00000135439, PIKE) encodes a neuronal ArfGAP and GTPase signaling scaffold implicated in postsynaptic PI3K/Akt survival and endosomal trafficking. "
        "Nominated from unadjusted postmortem prefrontal cortex (BA9) single-nucleus RNA-seq downregulation in ALS Layer 2/3 excitatory neurons, the hypothesis proposed restoring cortical AGAP2 signaling."
    ),
    "BA9-02": (
        "AP1G2 (ENSG00000213983) encodes the gamma-2 adaptin subunit of clathrin-associated adaptor complex AP-1 involved in trans-Golgi and endosomal cargo sorting. "
        "Nominated from unadjusted postmortem BA9 cortical snRNA-seq downregulation in ALS upper-layer excitatory neurons, the hypothesis proposed correcting endosomal sorting defects."
    ),
    "BA9-03": (
        "BRSK2 (ENSG00000174672, SAD-A) encodes an AMPK-related serine/threonine kinase governing neuronal polarization, axon specification, and presynaptic vesicle maturation. "
        "Nominated from unadjusted postmortem BA9 excitatory neuron snRNA-seq reductions, the hypothesis proposed rescuing cortical BRSK2 kinase activity in ALS."
    ),
    "BA9-04": (
        "DNAJB2 (ENSG00000135924, HSJ1) encodes a neuronal Hsp40 co-chaperone with two alternatively spliced isoforms: cytosolic DNAJB2a (ENST00000392086), which clears misfolded ubiquitylated TDP-43, and intron-9-retaining ER-prenylated DNAJB2b, with recessive human loss-of-function mutations causing distal motor neuropathy and juvenile ALS. "
        "Surviving as the sole GC-robust oligodendroglial and spinal lead from the BA9 cohort, the hypothesis tests enhancing intron-9 excision or augmenting cytosolic DNAJB2a."
    ),
    "BA9-05": (
        "KIFC2 (ENSG00000167702) encodes a C-terminal minus-end-directed kinesin-14 motor protein expressed in adult mammalian dendrites. "
        "Nominated from unadjusted postmortem BA9 excitatory neuron snRNA-seq downregulation, the hypothesis proposed restoring dendritic microtubule transport in ALS cortex."
    ),
    "BA9-06": (
        "MIB2 (ENSG00000197530, Mindbomb E3 ubiquitin protein ligase 2) encodes a RING-finger ubiquitin ligase regulating Notch ligand endocytosis and NF-kappaB signaling. "
        "Nominated from unadjusted postmortem BA9 Layer 2/3 excitatory snRNA-seq reduction, the hypothesis proposed rescuing cortical MIB2 ubiquitin-ligase activity."
    ),
    "BA9-07": (
        "MYO18A (ENSG00000196535) encodes an unconventional PDZ-containing myosin scaffold linking Golgi membranes to the actin cytoskeleton. "
        "Nominated from unadjusted postmortem BA9 oligodendrocyte snRNA-seq upregulation, the hypothesis proposed inhibiting glial MYO18A remodeling in ALS."
    ),
    "BA9-08": (
        "SNPH (ENSG00000101298) encodes syntaphilin, an outer-mitochondrial-membrane static anchor that clamps axonal mitochondria onto microtubules and halts kinesin-driven transport. "
        "Motivated by primary motor cortex RNA shifts, insoluble cortical protein accumulation, and enhanced neuromuscular junction outgrowth upon SNPH depletion in human assembloids (PMID:41193975), this exploratory hypothesis tests graded partial release of stalled axonal mitochondria."
    ),
    "BA9-09": (
        "ZNF783 (ENSG00000204946) encodes an uncharacterized KRAB-domain zinc-finger transcriptional regulator. "
        "Nominated solely from unadjusted postmortem BA9 Layer 2/3 excitatory neuron snRNA-seq reduction, the hypothesis posited loss of cortical transcriptional repression in sporadic ALS."
    ),
    "BA9-10": (
        "CAPG (ENSG00000042493) encodes gelsolin-like macrophage-capping protein, a Ca2+-sensitive actin-filament barbed-end capper enriched in myeloid cells and microglia. "
        "Nominated from bulk postmortem spinal cord and cortical homogenate elevation, the hypothesis proposed inhibiting microglial CAPG-mediated cytoskeletal activation in ALS."
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
        "Validated in the Phase 3 JETALS trial (NCT03548311, PMID:35532908) and approved in Japan for early-onset (<=12 months) ALS, it serves as an early-window clinical standard-of-care benchmark whose negative live-imaging screen readout highlights plausible Co-C photolability artifact risk."
    ),
    "S09": (
        "Censavudine (TPN-101, CHEMBL124363) is an oral nucleoside reverse transcriptase inhibitor of endogenous LINE-1 retrotransposons, which become derepressed upon nuclear TDP-43 loss in the ~13.5% cortical ALS-TE molecular subtype. "
        "Building on encouraging Phase 2a biomarker and vital-capacity signals in C9orf72-ALS (NCT04993755), this hypothesis tests extending LINE-1 reverse-transcriptase inhibition to sporadic ALS-TE patients identified via living-CSF cryptic-splicing and retroelement biomarkers."
    ),
    "DN-01": (
        "ATG4B (ENSG00000168397) encodes the primary mammalian cysteine protease (PDB 2Z0D) that primes pro-LC3B and recycles lipidated LC3-II to sustain neuronal autophagosome biogenesis. "
        "Nuclear TDP-43 depletion unmasks a frame-truncating cryptic exon after Glu319 that deletes the C-terminal LC3-interacting region and depletes cortical ATG4B protein; intrathecal steric splice-switching aims to restore autophagic proteostasis in motor neurons."
    ),
    "DN-02": (
        "KALRN (ENSG00000160145) encodes Kalirin, a dual-RhoGEF synaptic scaffold whose full-length Kalirin-12/DuET isoforms carry a C-terminal serine/threonine kinase domain regulating dendritic spine stability. "
        "TDP-43 loss induces high-penetrance intron-56 cryptic-exon inclusion across C9orf72-FTD/ALS cortex that truncates the C-terminal kinase domain (sparing shorter Kalirin-7); steric splice blockade tests whether restoring full-length Kalirin-12 rescues synaptic integrity."
    ),
    "DN-03": (
        "PTPRT (ENSG00000196090) encodes a CNS-restricted receptor protein tyrosine phosphatase that stabilizes trans-synaptic Neuroligin/paxillin adhesion complexes while dephosphorylating STAT3 Tyr705. "
        "Unbiased multi-cohort screening revealed severe translational Ribo-seq, cortical homogenate protein, and living-CSF PTPRT depletion upon TDP-43 pathology; this hypothesis tests fine-mapping and sterically blocking its intronic cryptic splicing event to restore synaptic adhesion."
    ),
    "DN-04": (
        "CELF5 (ENSG00000161082) encodes a brain- and motor-system-restricted CUGBP Elav-like RNA-binding factor that regulates neuron-specific alternative splicing. "
        "Depletion of nuclear TDP-43 induces inclusion of a 108-bp nonsense-mediated-decay cryptic exon (replicated at LeafCutter cluster clu_25763_+ in sporadic ALS patient iPSC motor neurons); intrathecal steric splice-switching aims to prevent secondary RNA-processing collapse downstream of TDP-43 loss."
    ),
    "DN-05": (
        "PRUNE2 (ENSG00000106772) encodes a large BNIP2-homology neuronal protein that suppresses RhoA–ROCK signaling to maintain motor axon caliber and prevent neurite retraction. "
        "Identified as the sole TDP-43 cryptic-splicing candidate significantly depleted across 55-um human ALS cervical anterior-horn MN-niche Visium spots alongside C9-FTD synaptosomal protein loss, the hypothesis tests resolving and sterically rescuing its mis-spliced junction."
    ),
    "DN-06": (
        "PFKP (ENSG00000067057) encodes the platelet isoform of phosphofructokinase-1, the rate-limiting allosteric gatekeeper partitioning neuronal glucose between glycolytic ATP generation and the antioxidant pentose phosphate pathway (PPP). "
        "TDP-43 loss induces cryptic-exon NMD and synaptosomal PFKP protein depletion; steric splice rescue tests whether restoring synaptic glycolysis improves bioenergetics without draining protective PPP NADPH/glutathione reserves."
    ),
    "DN-07": (
        "TRAPPC12 (ENSG00000171853) encodes an outer subunit of the TRAPPIII tethering complex essential for ER-to-Golgi transport and early autophagosome assembly upstream of YKT6. "
        "Nuclear TDP-43 depletion activates a pathology-selective intronic alternative last exon (ALE) that prematurely truncates TRAPPC12 translation; steric blockade of the cryptic 3' splice site tests restoring full-length secretory and autophagic trafficking."
    ),
    "DN-08": (
        "ELK1 (ENSG00000126767) encodes an ERK-responsive ETS transcription factor with compartment-dependent polarity: nuclear SRF co-activation supports neuronal survival, whereas dendritic ELK1 translation promotes apoptosis. "
        "Because TDP-43 loss derepresses a 3.90-kb terminal 3'-UTR extension that elevates ELK1 translation (while nuclear RNase-H1 gapmers risk Pol II readthrough cleavage of canonical ELK1), this exploratory hypothesis tests steric distal-PAS blockade or cytoplasmic 3'-extension siRNA to adjudicate neuroprotective vs. pro-apoptotic polarity."
    ),
    "DN-09": (
        "DLGAP1 (ENSG00000170579, GKAP) encodes a core postsynaptic density scaffold linking glutamate receptor-associated PSD-95 complexes to Shank cytoskeleton assemblies. "
        "Unbiased TDP-43 cryptic-polyadenylation discovery identified a pathology-selective intronic alternative last exon paired with cortical synaptosomal DLGAP1 protein loss; steric 3'-splice-site blockade tests rescuing excitatory postsynaptic scaffold integrity."
    ),
    "DN-10": (
        "DPP6 (ENSG00000130226) encodes a catalytically inactive dipeptidyl-peptidase-like transmembrane auxiliary subunit (PDB 1XFD) that assembles with somatodendritic Kv4.2 A-type potassium channels to regulate dendritic excitability. "
        "Identified as the most strongly depleted de novo protein in living ALS patient CSF alongside cortical synaptosome loss, it serves as a non-therapeutic fluid pharmacodynamic biomarker tracking somatodendritic membrane attrition."
    ),
    "DN-11": (
        "DPP10 (ENSG00000175497) encodes a catalytically inactive neuronal Kv4 potassium-channel auxiliary subunit paralogous to DPP6 that governs somatodendritic A-type current gating. "
        "Co-depleted with DPP6 in living ALS patient CSF DIA proteomics and primary motor cortex excitatory neurons, it serves as a companion fluid biomarker of somatodendritic attrition rather than an enzymatic drug target."
    ),
    "DN-12": (
        "CFL1 (ENSG00000172757) encodes cofilin-1, a pan-essential actin-severing protein that forms stress-induced cofilin-actin rods in ATP-depleted degenerating motor axons. "
        "Consistently elevated across independent living ALS CSF TMT and DIA proteomic cohorts while cellularly pan-essential, CFL1 serves as a fluid axonal-cytoskeletal damage biomarker rather than an inhibition target."
    ),
    "DN-13": (
        "MAOB (ENSG00000069535) encodes outer-mitochondrial-membrane monoamine oxidase B, an H2O2-generating flavoprotein predominantly expressed in astrocytes. "
        "Nominated from postmortem spinal spatial transcriptomic and cortical homogenate increases, its therapeutic hypothesis proposed irreversible MAO-B inhibition (rasagiline/selegiline class, NCT01879241) to curb glial oxidative stress in ALS."
    ),
    "DN-14": (
        "PMX 205 (CHEMBL5653589) is a cyclic hexapeptide allosteric antagonist of the complement C5a anaphylatoxin receptor C5aR1 (ENSG00000197405). "
        "Identified as the top unadopted nominal survival candidate (#9/107, sub-FDR q=0.070 in C5a-free monocultures) in sporadic ALS patient iPSC motor neuron screening without a completed human C5aR1 ALS efficacy trial, this exploratory hypothesis tests whether selective C5aR1 blockade (sparing C5L2 and terminal C5b-9) acts on-target in MN-microglia co-cultures despite upstream clinical C5 failures."
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
        "Acetylcysteine (N-acetylcysteine) is a systemic thiol-donor prodrug of intracellular glutathione and a direct scavenger of extracellular reactive oxygen species. "
        "Re-emerging as a nominal survival hit in 2.5 uM sporadic ALS iPSC motor neuron screening, its hypothesis proposed systemic thiol replenishment to counteract motor neuron oxidative stress (PMID:7763202)."
    ),
    "DN-18": (
        "Coenzyme Q10 (ubiquinone) is an inner-mitochondrial-membrane electron carrier between Complexes I/II and Complex III that also acts as a lipid-soluble antioxidant. "
        "Nominated from marginal survival extension in sporadic ALS iPSC motor neuron screening, its hypothesis proposed high-dose oral supplementation to rescue motor neuron bioenergetics and lipid peroxidation (NCT00243932, PMID:19743457)."
    ),
    "DN-19": (
        "L-Serine is a neurotrophic amino acid and obligate substrate of serine palmitoyltransferase whose supplementation competitively suppresses synthesis of neurotoxic 1-deoxysphingolipids. "
        "Crossing the human ALS blood-brain barrier in Phase 1 (NCT01835782) while its open-label Phase 2 study (NCT03580616) ended administratively rather than for clinical futility, the hypothesis requires serine-defined media deconvolution to separate metabolic efficacy from basal-media noise."
    ),
}
