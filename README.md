# Semantic and Spatial Matching Visual Place Recognition (SSM-VPR)
This is the official repository for the SSM-VPR methodology presented in the following papers:

*[Spatio-Semantic ConvNet-Based Visual Place Recognition](https://arxiv.org/abs/1909.07671)*

*[Highly Robust Visual Place Recognition Through Spatial Matching of CNN Features](https://www.researchgate.net/publication/335715895_Highly_Robust_Visual_Place_Recognition_Through_Spatial_Matching_of_CNN_Features)*

*[Visual Place Recognition by Spatial Matching of High-level CNN Features](https://www.researchgate.net/publication/338841595_Visual_Place_Recognition_by_Spatial_Matching_of_High-level_CNN_Features)*

We propose a visual place recognition (VPR) pipeline 
that achieves  substantially improved precision as compared with approaches commonly appearing in the literature. 
It is based on a standard image retrieval configuration, with an initial stage that retrieves the closest candidates 
to a query from a database and a second stage where the list of candidates is re-ranked. 
The latter is realized by the introduction of a novel geometric verification procedure that uses the activations of a 
pre-trained convolutional neural network. It is both remarkably simple and robust to viewpoint and condition changes. 
As a stand-alone, general spatial matching methodology, it could be easily added and used to enhance existing  VPR 
approaches whose output is a ranked list of candidates. The proposed two-stage pipeline is also improved through extensive 
optimization of hyperparameters and by the implementation of a frame-based temporal filter that takes into account past 
recognition results.

This system is summarized in the following diagram:
<p align="center">
  <img src="images/SSM_workflow.png" width="80%"/>
  <br /><em>System's flowchart</em>
</p>

