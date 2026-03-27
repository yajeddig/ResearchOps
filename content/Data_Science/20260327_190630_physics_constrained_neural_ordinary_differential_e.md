---
title: "Physics-constrained neural ordinary differential equation models to discover and predict microbial community dynamics"
date: 2026-03-27
category: Data_Science
confidence: 0.95
tags: ['physics-constrained models', 'neural ordinary differential equations', 'microbial community dynamics', 'machine learning', 'mechanistic modeling', 'hybrid models', 'interpretability', 'predictive modeling', 'systems biology', 'metabolite dynamics', 'biotechnology', 'sector:wwtp', 'sector:biogas', 'sector:pharma']
source: "https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1"
type: Article
source_type: Paper
hash: 190630
---

## 🎯 Relevance
This research offers a significant advancement for industrial applications involving microbial communities (e.g., wastewater treatment, biogas production, biopharmaceutical manufacturing, food fermentation). By providing more accurate and interpretable predictive models, it enables better process understanding, optimization, control, and rational design of microbial systems, leading to improved efficiency, reduced costs, and enhanced product quality. It's a valuable learning opportunity for applying hybrid modeling (mechanistic + ML) in complex biological process engineering.

## 📖 Content
# Physics-constrained neural ordinary differential equation models to discover and predict microbial community dynamics | bioRxiv

[Skip to main content](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1#main-content)

[![Image 1: bioRxiv](https://www.biorxiv.org/sites/default/files/biorxiv_article_logo.jpg)](https://www.biorxiv.org/)

*   [Home](https://www.biorxiv.org/)
*   [Submit](https://www.biorxiv.org/submit-a-manuscript)
*   [FAQ](https://www.biorxiv.org/about/FAQ)
*   [Blog](https://connect.biorxiv.org/news/)
*   [ALERTS / RSS](https://www.biorxiv.org/content/alertsrss)
*   [Resources](https://connect.biorxiv.org/resources/)
*   [About](https://www.biorxiv.org/content/about-biorxiv)
*   [Channels](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1#)
    *   [4D Nucleome](https://connect.biorxiv.org/relate/content/66)
    *   [Academia Sinica](https://connect.biorxiv.org/group/content/38)
    *   [Advances in Genome Biology and Technology (AGBT) General Meeting 2016 #AGBT16](https://connect.biorxiv.org/relate/content/10)
    *   [Albert Einstein College of Medicine](https://connect.biorxiv.org/group/content/4)
    *   [Aligning Science Across Parkinson's (ASAP)](https://connect.biorxiv.org/relate/content/195)
    *   [Allen Institute for Cell Science](https://connect.biorxiv.org/relate/content/71)
    *   [Arc Institute](https://connect.biorxiv.org/relate/content/224)
    *   [Babraham Institute](https://connect.biorxiv.org/relate/content/197)
    *   [BICCN/BICAN](https://connect.biorxiv.org/relate/content/208)
    *   [BioImaging North America](https://connect.biorxiv.org/relate/content/194)
    *   [Biology of Genomes 2016 #BOG16](https://connect.biorxiv.org/relate/content/19)
    *   [Breakthrough Discoveries for Thriving with Bipolar Disorder](https://connect.biorxiv.org/relate/content/236)
    *   [Brown University](https://connect.biorxiv.org/group/content/9)
    *   [California Institute of Technology](https://connect.biorxiv.org/group/content/32)
    *   [Carnegie Mellon University](https://connect.biorxiv.org/group/content/19)
    *   [Case Western Reserve University](https://connect.biorxiv.org/group/content/36)
    *   [Central Oxford Structural Microscopy and Imaging](https://connect.biorxiv.org/relate/content/143)
    *   [Centre for Microbiology and Environmental Systems Science](https://connect.biorxiv.org/relate/content/190)
    *   [Chan Zuckerberg Biohub](https://connect.biorxiv.org/relate/content/121)
    *   [Columbia University](https://connect.biorxiv.org/group/content/27)
    *   [Donders Institute for Brain, Cognition and Behaviour](https://connect.biorxiv.org/relate/content/184)
    *   [DREAM](https://connect.biorxiv.org/relate/content/153)
    *   [Drug Development and Clinical Therapeutics](https://connect.biorxiv.org/relate/content/52)
    *   [ENCODE](https://connect.biorxiv.org/relate/content/177)
    *   [Ernst Strüngmann Institute (ESI) for Neuroscience](https://connect.biorxiv.org/relate/content/211)
    *   [European Molecular Biology Laboratory (EMBL)](https://connect.biorxiv.org/relate/content/159)
    *   [Francis Crick Institute](https://connect.biorxiv.org/relate/content/88)
    *   [Fred Hutchinson Cancer Center](https://connect.biorxiv.org/group/content/28)
    *   [Georgia Institute of Technology](https://connect.biorxiv.org/group/content/20)
    *   [Harvard Program in Therapeutic Sciences](https://connect.biorxiv.org/relate/content/151)
    *   [The Howard Hughes Medical Institute (HHMI)](https://connect.biorxiv.org/relate/content/227)
    *   [Human Cell Atlas](https://connect.biorxiv.org/relate/content/163)
    *   [Human Pangenome Reference Consortium (HPRC)](https://connect.biorxiv.org/relate/content/215)
    *   [IMO Workshop](https://connect.biorxiv.org/relate/content/8)
    *   [Impact of Genomic Variation on Function (IGVF)](https://connect.biorxiv.org/relate/content/214)
    *   [Institut Pasteur](https://connect.biorxiv.org/relate/content/235/channel)
    *   [Institute of Science and Technology Austria](https://connect.biorxiv.org/group/content/12)
    *   [International Human Epigenome Consortium (IHEC)](https://connect.biorxiv.org/relate/content/219)
    *   [International Mouse Phenotyping Consortium (IMPC)](https://connect.biorxiv.org/relate/content/185)
    *   [Iowa State University](https://connect.biorxiv.org/group/content/6)
    *   [Johns Hopkins University](https://connect.biorxiv.org/group/content/47)
    *   [Mathematical Oncology](https://connect.biorxiv.org/relate/content/1)
    *   [Micron Oxford](https://connect.biorxiv.org/relate/content/116)
    *   [Michigan State University](https://connect.biorxiv.org/group/content/7)
    *   [Morgridge Institute](https://connect.biorxiv.org/group/content/57)
    *   [National Taiwan University](https://connect.biorxiv.org/group/content/39)
    *   [NCI Cancer Systems Biology Consortium](https://connect.biorxiv.org/relate/content/210)
    *   [NF Open Science Initiative](https://connect.biorxiv.org/relate/content/213)
    *   [NCI Human Tumor Atlas Network](https://connect.biorxiv.org/relate/content/171)
    *   [Neuromatch Conference](https://connect.biorxiv.org/relate/content/209)
    *   [NeurotechEU](https://connect.biorxiv.org/relate/content/189)
    *   [North Carolina State University](https://connect.biorxiv.org/group/content/37)
    *   [Northeastern University](https://connect.biorxiv.org/group/content/54)
    *   [Oregon Health & Sciences University](https://connect.biorxiv.org/group/content/22)
    *   [RNA Therapeutics Institute at UMass Chan Med School](https://connect.biorxiv.org/relate/content/243)
    *   [Rosetta Commons](https://connect.biorxiv.org/relate/content/191)
    *   [Rutgers University](https://connect.biorxiv.org/group/content/31)
    *   [SeroNet](https://connect.biorxiv.org/relate/content/192)
    *   [Simons Foundation Autism Research Initiative (SFARI)](https://connect.biorxiv.org/relate/content/74)
    *   [Society for Molecular Biology and Evolution #SMBE2016](https://connect.biorxiv.org/relate/content/29)
    *   [Somatic Cell Genome Editing Program](https://connect.biorxiv.org/relate/content/167)
    *   [Somatic Mosaicism across the Human Tissues Network](https://connect.biorxiv.org/relate/content/222)
    *   [SPARC](https://connect.biorxiv.org/relate/content/187)
    *   [Stowers Institute for Medical Research](https://connect.biorxiv.org/group/content/3)
    *   [Stockholm University](https://connect.biorxiv.org/group/content/14)
    *   [Tel Aviv University](https://connect.biorxiv.org/group/content/8)
    *   [The Michael J. Fox Foundation](https://connect.biorxiv.org/relate/content/207)
    *   [The Rockefeller University](https://connect.biorxiv.org/group/content/2)
    *   [The Sainsbury Laboratory](https://connect.biorxiv.org/relate/content/98)
    *   [The Whitehead Institute](https://connect.biorxiv.org/relate/content/212)
    *   [University of Connecticut Health Center](https://connect.biorxiv.org/group/content/16)
    *   [University of California, Berkeley](https://connect.biorxiv.org/group/content/13)
    *   [University of California, San Diego](https://connect.biorxiv.org/group/content/41)
    *   [University of California, San Francisco](https://connect.biorxiv.org/group/content/10)
    *   [University of Chicago](https://connect.biorxiv.org/group/content/42)
    *   [University of Geneva](https://connect.biorxiv.org/group/content/26)
    *   [University of Guelph](https://connect.biorxiv.org/group/content/23)
    *   [University of Hong Kong](https://connect.biorxiv.org/group/content/29)
    *   [University of Illinois Chicago](https://connect.biorxiv.org/group/content/43)
    *   [University of Iowa](https://connect.biorxiv.org/group/content/24)
    *   [University of Kansas](https://connect.biorxiv.org/group/content/33)
    *   [University of Massachusetts Chan Medical School](https://connect.biorxiv.org/group/content/44)
    *   [University of New South Wales](https://connect.biorxiv.org/group/content/25)
    *   [University of Ottawa](https://connect.biorxiv.org/group/content/35)
    *   [University of Sydney](https://connect.biorxiv.org/group/content/50)
    *   [Vanderbilt University](https://connect.biorxiv.org/group/content/30)
    *   [Vienna BioCenter](https://connect.biorxiv.org/relate/content/186)
    *   [Washington University in St. Louis](https://connect.biorxiv.org/group/content/11)
    *   [Weizmann Institute of Science](https://connect.biorxiv.org/group/content/15)
    *   [Yale University](https://connect.biorxiv.org/group/content/53)

Search for this keyword  

[Advanced Search](https://www.biorxiv.org/search)

[](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)

 New Results [Follow this preprint](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)
# Physics-constrained neural ordinary differential equation models to discover and predict microbial community dynamics

Jaron Thompson, Bryce M.Connors, Victor M.Zavala, [View ORCID Profile](http://orcid.org/0000-0003-2200-1963)Ophelia S.Venturelli

doi: https://doi.org/10.1101/2025.07.08.663743 

This article is a preprint and has not been certified by peer review [[what does this mean?](https://www.biorxiv.org/about/FAQ#unrefereed)].

Jaron Thompson 

1 Department of Chemical and Biological Engineering, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

2 Department of Biochemistry, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

*   [Find this author on Google Scholar](https://www.biorxiv.org/lookup/google-scholar?link_type=googlescholar&gs_type=author&author%5B0%5D=Jaron%2BThompson%2B "Open in new tab")
*   [Find this author on PubMed](https://www.biorxiv.org/lookup/external-ref?access_num=Thompson%20J&link_type=AUTHORSEARCH "Open in new tab")
*   [Search for this author on this site](https://www.biorxiv.org/search/author1%3AJaron%2BThompson%2B)

Bryce M. Connors 

1 Department of Chemical and Biological Engineering, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

2 Department of Biochemistry, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

*   [Find this author on Google Scholar](https://www.biorxiv.org/lookup/google-scholar?link_type=googlescholar&gs_type=author&author%5B0%5D=Bryce%2BM.%2BConnors%2B "Open in new tab")
*   [Find this author on PubMed](https://www.biorxiv.org/lookup/external-ref?access_num=Connors%20BM&link_type=AUTHORSEARCH "Open in new tab")
*   [Search for this author on this site](https://www.biorxiv.org/search/author1%3ABryce%2BM.%2BConnors%2B)

Victor M. Zavala 

1 Department of Chemical and Biological Engineering, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

*   [Find this author on Google Scholar](https://www.biorxiv.org/lookup/google-scholar?link_type=googlescholar&gs_type=author&author%5B0%5D=Victor%2BM.%2BZavala%2B "Open in new tab")
*   [Find this author on PubMed](https://www.biorxiv.org/lookup/external-ref?access_num=Zavala%20VM&link_type=AUTHORSEARCH "Open in new tab")
*   [Search for this author on this site](https://www.biorxiv.org/search/author1%3AVictor%2BM.%2BZavala%2B)

Ophelia S. Venturelli 

1 Department of Chemical and Biological Engineering, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

2 Department of Biochemistry, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

3 Department of Bacteriology, University of Wisconsin-Madison, Madison, Wisconsin, United States of America

4 Department of Biomedical Engineering, Duke University, Durham, North Carolina, United States of America

*   [Find this author on Google Scholar](https://www.biorxiv.org/lookup/google-scholar?link_type=googlescholar&gs_type=author&author%5B0%5D=Ophelia%2BS.%2BVenturelli%2B "Open in new tab")
*   [Find this author on PubMed](https://www.biorxiv.org/lookup/external-ref?access_num=Venturelli%20OS&link_type=AUTHORSEARCH "Open in new tab")
*   [Search for this author on this site](https://www.biorxiv.org/search/author1%3AOphelia%2BS.%2BVenturelli%2B)
*   [ORCID record for Ophelia S. Venturelli](http://orcid.org/0000-0003-2200-1963 "Open in new tab")
*   For correspondence: [ophelia.venturelli@duke.edu](mailto:ophelia.venturelli@duke.edu)

*   [Abstract](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)[](https://www.biorxiv.org/panels_ajax_tab/biorxiv_tab_art/node:4741028/1)
*   [Full Text](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1.full-text)[](https://www.biorxiv.org/panels_ajax_tab/article_tab_full_text/node:4741028/1)
*   [Info/History](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1.article-info)[](https://www.biorxiv.org/panels_ajax_tab/biorxiv_tab_info/node:4741028/1)
*   [Metrics](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1.article-metrics)[](https://www.biorxiv.org/panels_ajax_tab/article_tab_metrics/node:4741028/1)
*   [Supplementary material](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1.supplementary-material)[](https://www.biorxiv.org/panels_ajax_tab/biorxiv_tab_data/node:4741028/1)
*   [Preview PDF](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1.full.pdf+html)[](https://www.biorxiv.org/panels_ajax_tab/biorxiv_tab_pdf/node:4741028/1)

![Image 2: Loading](https://www.biorxiv.org/sites/all/modules/contrib/panels_ajax_tab/images/loading.gif)

## Abstract

Microbial communities play essential roles in shaping ecosystem functions and predictive modeling frameworks are crucial for understanding, controlling, and harnessing their properties. Competition and cross-feeding of metabolites drives microbiome dynamics and functions. Existing mechanistic models that capture metabolite-mediated interactions in microbial communities have limited flexibility due to rigid assumptions. While machine learning models provide flexibility, they require large datasets, are challenging to interpret, and can over-fit to experimental noise. To overcome these limitations, we develop a physics-constrained machine learning model, which we call the Neural Species Mediator (NSM), that combines a mechanistic model of metabolite dynamics with a machine learning component. The NSM is more accurate than mechanistic or machine learning components on experimental datasets and provides insights into direct biological interactions. In summary, embedding a neural network into a mechanistic model of microbial community dynamics improves prediction performance and interpretability compared to its constituent mechanistic or machine learning components.

**Significance statement** Microbial communities drive essential biological processes in every ecosystem. Predicting microbial community dynamics and functions and uncovering their interaction networks are challenging due to their complexity and emergent interactions. We develop a framework that combines biological knowledge with machine learning to accurately predict community and metabolite dynamics. This approach outperforms existing ecological and machine learning models by capturing environmentally mediated interactions while providing interpretable insights into microbe-metabolite interactions. Our framework enables the rational design and control of microbial communities for applications in medicine, agriculture and biotechnology

### Competing Interest Statement

The authors have declared no competing interest.

Copyright

The copyright holder for this preprint is the author/funder, who has granted bioRxiv a license to display the preprint in perpetuity. It is made available under a [CC-BY-NC-ND 4.0 International license](http://creativecommons.org/licenses/by-nc-nd/4.0/).

bioRxiv and medRxiv thank the following for their generous financial support:
> The Chan Zuckerberg Initiative, Cold Spring Harbor Laboratory, the Sergey Brin Family Foundation, California Institute of Technology, Centre National de la Recherche Scientifique, Fred Hutchinson Cancer Center, Imperial College London, Massachusetts Institute of Technology, Stanford University, The University of Edinburgh, University of Washington, and Vrije Universiteit Amsterdam.

[Back to top](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1#page)

[Previous](https://www.biorxiv.org/content/10.1101/2025.07.10.663745v1 "A new phylogeny and phylogenetic classification for Solanaceae")[Next](https://www.biorxiv.org/content/10.1101/2025.07.11.664500v1 "A Portable RPA-CRISPR/Cas12a-Based Biosensing Platform for On-Site Detection of the Microcystin Synthetase E Gene in Lake Water")

 Posted July 12, 2025. 

[Download PDF](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1.full.pdf)

[Print/Save Options](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)

[Download PDF](https://www.biorxiv.org/content/biorxiv/early/2025/07/12/2025.07.08.663743.full.pdf)[Full Text & In-line Figures](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)[XML](https://www.biorxiv.org/content/biorxiv/early/2025/07/12/2025.07.08.663743.source.xml)

[More Info](https://www.biorxiv.org/about/FAQ#PrintOptions "More Information on Print/Save Options")

[Supplementary Material](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1.supplementary-material)

[Email](https://www.biorxiv.org/ "Email this Article")

[Share](https://www.biorxiv.org/)

Physics-constrained neural ordinary differential equation models to discover and predict microbial community dynamics

Jaron Thompson, Bryce M.Connors, Victor M.Zavala, Ophelia S.Venturelli

bioRxiv 2025.07.08.663743; doi: https://doi.org/10.1101/2025.07.08.663743 

This article is a preprint and has not been certified by peer review [[what does this mean?](https://www.biorxiv.org/about/FAQ#unrefereed)].

Share This Article: Copy

[![Image 3: Twitter logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/twitter.png)](https://www.biorxiv.org/highwire_log/share/twitter?link=http%3A%2F%2Ftwitter.com%2Fshare%3Furl%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.1101%2F2025.07.08.663743v1%26text%3DPhysics-constrained%2520neural%2520ordinary%2520differential%2520equation%2520models%2520to%2520discover%2520and%2520predict%2520microbial%2520community%2520dynamics "Share this on Twitter")[![Image 4: Facebook logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/fb-blue.png)](https://www.biorxiv.org/highwire_log/share/facebook?link=http%3A%2F%2Fwww.facebook.com%2Fsharer.php%3Fu%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.1101%2F2025.07.08.663743v1%26t%3DPhysics-constrained%2520neural%2520ordinary%2520differential%2520equation%2520models%2520to%2520discover%2520and%2520predict%2520microbial%2520community%2520dynamics "Share on Facebook")[![Image 5: LinkedIn logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/linkedin-32px.png)](https://www.biorxiv.org/highwire_log/share/linkedin?link=http%3A%2F%2Fwww.linkedin.com%2FshareArticle%3Fmini%3Dtrue%26url%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.1101%2F2025.07.08.663743v1%26title%3DPhysics-constrained%2520neural%2520ordinary%2520differential%2520equation%2520models%2520to%2520discover%2520and%2520predict%2520microbial%2520community%2520dynamics%26summary%3D%26source%3DbioRxiv "Publish this post to LinkedIn")[![Image 6: Mendeley logo](https://www.biorxiv.org/sites/all/modules/highwire/highwire/images/mendeley.png)](https://www.biorxiv.org/highwire_log/share/mendeley?link=http%3A%2F%2Fwww.mendeley.com%2Fimport%2F%3Furl%3Dhttps%253A%2F%2Fwww.biorxiv.org%2Fcontent%2F10.1101%2F2025.07.08.663743v1%26title%3DPhysics-constrained%2520neural%2520ordinary%2520differential%2520equation%2520models%2520to%2520discover%2520and%2520predict%2520microbial%2520community%2520dynamics "Share on Mendeley")

[Citation Tools](https://www.biorxiv.org/ "Citation Tools")

[Get QR code](https://connect.biorxiv.org/qr/2025.07.08.663743)

*    

## Subject Area

*   [Systems Biology](https://www.biorxiv.org/collection/systems-biology)

Reviews and Context

0

Comment

0

TRIP Peer Reviews

0

Community Reviews

0

Automated Services

0

Blogs/Media

0

Author Videos

**Subject Areas**

[**All Articles**](https://www.biorxiv.org/content/early/recent)

*   [Animal Behavior and Cognition](https://www.biorxiv.org/collection/animal-behavior-and-cognition)(7461) 
*   [Biochemistry](https://www.biorxiv.org/collection/biochemistry)(17142) 
*   [Bioengineering](https://www.biorxiv.org/collection/bioengineering)(13401) 
*   [Bioinformatics](https://www.biorxiv.org/collection/bioinformatics)(40688) 
*   [Biophysics](https://www.biorxiv.org/collection/biophysics)(20889) 
*   [Cancer Biology](https://www.biorxiv.org/collection/cancer-biology)(18007) 
*   [Cell Biology](https://www.biorxiv.org/collection/cell-biology)(24804) 
*   [Clinical Trials](https://www.biorxiv.org/collection/clinical-trials)(138) 
*   [Developmental Biology](https://www.biorxiv.org/collection/developmental-biology)(13078) 
*   [Ecology](https://www.biorxiv.org/collection/ecology)(19409) 
*   [Epidemiology](https://www.biorxiv.org/collection/epidemiology)(2067) 
*   [Evolutionary Biology](https://www.biorxiv.org/collection/evolutionary-biology)(23821) 
*   [Genetics](https://www.biorxiv.org/collection/genetics)(15337) 
*   [Genomics](https://www.biorxiv.org/collection/genomics)(22012) 
*   [Immunology](https://www.biorxiv.org/collection/immunology)(17266) 
*   [Microbiology](https://www.biorxiv.org/collection/microbiology)(39359) 
*   [Molecular Biology](https://www.biorxiv.org/collection/molecular-biology)(16697) 
*   [Neuroscience](https://www.biorxiv.org/collection/neuroscience)(86288) 
*   [Paleontology](https://www.biorxiv.org/collection/paleontology)(654) 
*   [Pathology](https://www.biorxiv.org/collection/pathology)(2762) 
*   [Pharmacology and Toxicology](https://www.biorxiv.org/collection/pharmacology-and-toxicology)(4678) 
*   [Physiology](https://www.biorxiv.org/collection/physiology)(7426) 
*   [Plant Biology](https://www.biorxiv.org/collection/plant-biology)(14717) 
*   [Scientific Communication and Education](https://www.biorxiv.org/collection/scientific-communication-and-education)(2015) 
*   [Synthetic Biology](https://www.biorxiv.org/collection/synthetic-biology)(4165) 
*   [Systems Biology](https://www.biorxiv.org/collection/systems-biology)(9596) 
*   [Zoology](https://www.biorxiv.org/collection/zoology)(2221) 

Reviews and Context x

Comments 0 TRiP 0 Community 0 Automated 0 Blogs/Media 0 Video 0

Comments

bioRxiv aims to provide a venue for anyone to comment on a bioRxiv preprint. Comments are moderated for offensive or irrelevant content (this can take ~24 h). Please avoid duplicate submissions and read our [Comment Policy](https://connect.biorxiv.org/news/2022/03/21/commenting_on_preprints) before commenting. The content of a comment is not endorsed by bioRxiv.

[Share this comments tab (click to copy link)](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)Copied!

TRiP

bioRxiv partners with journals and review services to enable posting of peer reviews and editorial decisions related to preprints they are evaluating. Reviews are posted with the consent of the authors.

TRiP reviews are part of a peer review pilot project in which participating organizations post peer reviews of manuscripts they are evaluating

_There is no TRiP material for this paper._

Community Reviews

bioRxiv aims to inform readers about online discussion of this preprint occurring elsewhere. The content at the links below is not endorsed by either bioRxiv or the preprint's authors.

Community reviews for this article:

_There are no community reviews for this paper._

Automated Services

A variety of services now perform automated analyses of papers. Outputs from automated tools that summarize and extract information from bioRxiv preprints using AI and other technologies are displayed below. Note these tools can generate errors and the information has not been verified by bioRxiv or the authors.

Automated Services:

_There are no automated services for this paper._

Blog/Media Links

bioRxiv aims to inform readers about online discussion of this preprint occurring elsewhere. The content at the links below is not endorsed by either bioRxiv or the preprint's authors.

Video

bioRxiv partners with conferences and institutions to display recordings of talks and seminars related to preprints. These are posted with the consent of the authors.

Video:

_There are no videos for this paper._

Powered by

[![Image 7](https://connect.biorxiv.org/eval/hypothesis.png)](https://web.hypothes.is/)

Powered by

[![Image 8](https://connect.biorxiv.org/eval/altmetric.png)](https://www.altmetric.com/)

## Follow this preprint

[X](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)

You can now receive automatic notifications when a preprint is revised, withdrawn, commented on, peer reviewed, or published in a journal. Select the events you would like to follow below and click "Submit". To see all of the preprints you are currently following, please go to the [bioRxiv Alerts Page](https://biorxiv.org/alerts).

Sign In to Follow this Preprint

Email * 

Email this Article close

Thank you for your interest in spreading the word about bioRxiv.

NOTE: Your email address is requested solely to identify you as the sender of this article.

Your Email * 

Your Name * 

Send To * 

Enter multiple addresses on separate lines or separate them with commas.

You are going to email the following  [Physics-constrained neural ordinary differential equation models to discover and predict microbial community dynamics](https://www.biorxiv.org/content/10.1101/2025.07.08.663743v1)

Message Subject   (Your Name) has forwarded a page to you from bioRxiv 

Message Body   (Your Name) thought you would like to see this page from the bioRxiv website. 

Your Personal Message  

CAPTCHA

This question is for testing whether or not you are a human visitor and to prevent automated spam submissions.

Citation Tools close

Physics-constrained neural ordinary differential equation models to discover and predict microbial community dynamics

Jaron Thompson, Bryce M.Connors, Victor M.Zavala, Ophelia S.Venturelli

bioRxiv 2025.07.08.663743; doi: https://doi.org/10.1101/2025.07.08.663743 

This article is a preprint and has not been certified by peer review [[what does this mean?](https://www.biorxiv.org/about/FAQ#unrefereed)].

## Citation Manager Formats

*   [BibTeX](https://www.biorxiv.org/highwire/citation/4741028/bibtext)
*   [Bookends](https://www.biorxiv.org/highwire/citation/4741028/bookends)
*   [EasyBib](https://www.biorxiv.org/highwire/citation/4741028/easybib)
*   [EndNote (tagged)](https://www.biorxiv.org/highwire/citation/4741028/endnote-tagged)
*   [EndNote 8 (xml)](https://www.biorxiv.org/highwire/citation/4741028/endnote-8-xml)
*   [Medlars](https://www.biorxiv.org/highwire/citation/4741028/medlars)
*   [Mendeley](https://www.biorxiv.org/highwire/citation/4741028/mendeley)
*   [Papers](https://www.biorxiv.org/highwire/citation/4741028/papers)
*   [RefWorks Tagged](https://www.biorxiv.org/highwire/citation/4741028/refworks-tagged)
*   [Ref Manager](https://www.biorxiv.org/highwire/citation/4741028/reference-manager)
*   [RIS](https://www.biorxiv.org/highwire/citation/4741028/ris)
*   [Zotero](https://www.biorxiv.org/highwire/citation/4741028/zotero)

We use cookies on this site to enhance your user experience. By clicking any link on this page you are giving your consent for us to set cookies.

Continue Find out more

## Abstract

Microbial communities play essential roles in shaping ecosystem functions and predictive modeling frameworks are crucial for understanding, controlling, and harnessing their properties. Competition and cross-feeding of metabolites drives microbiome dynamics and functions. Existing mechanistic models that capture metabolite-mediated interactions in microbial communities have limited flexibility due to rigid assumptions. While machine learning models provide flexibility, they require large datasets, are challenging to interpret, and can over-fit to experimental noise. To overcome these limitations, we develop a physics-constrained machine learning model, which we call the Neural Species Mediator (NSM), that combines a mechanistic model of metabolite dynamics with a machine learning component. The NSM is more accurate than mechanistic or machine learning components on experimental datasets and provides insights into direct biological interactions. In summary, embedding a neural network into a mechanistic model of microbial community dynamics improves prediction performance and interpretability compared to its constituent mechanistic or machine learning components.

**Significance statement** Microbial communities drive essential biological processes in every ecosystem. Predicting microbial community dynamics and functions and uncovering their interaction networks are challenging due to their complexity and emergent interactions. We develop a framework that combines biological knowledge with machine learning to accurately predict community and metabolite dynamics. This approach outperforms existing ecological and machine learning models by capturing environmentally mediated interactions while providing interpretable insights into microbe-metabolite interactions. Our framework enables the rational design and control of microbial communities for applications in medicine, agriculture and biotechnology

## 💡 Key Insights
- Existing mechanistic models for microbial communities have limited flexibility due to rigid assumptions.
- Traditional machine learning models for microbial communities require large datasets, are challenging to interpret, and can over-fit to noise.
- The Neural Species Mediator (NSM) is a novel physics-constrained machine learning model that combines a mechanistic model of metabolite dynamics with a neural network.
- NSM demonstrates improved prediction performance and interpretability compared to purely mechanistic or purely machine learning models on experimental datasets.
- The framework provides insights into direct biological interactions and enables rational design and control of microbial communities for applications in medicine, agriculture, and biotechnology.

## 📚 References
- Jaron Thompson, Bryce M.Connors, Victor M.Zavala, Ophelia S.Venturelli, Physics-constrained neural ordinary differential equation models to discover and predict microbial community dynamics, bioRxiv, 2025, https://doi.org/10.1101/2025.07.08.663743 *(source)*

## 🏷️ Classification
The content describes a novel hybrid modeling approach (mechanistic + machine learning, specifically Neural ODEs) for predicting and understanding complex biological systems (microbial communities), which falls squarely within advanced data science methodologies for industrial applications.
