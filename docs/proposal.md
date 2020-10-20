---
layout: default
title: Proposal
---
## Project Summary

We consider the problem of generating environment aware, style specific text snippets in Minecraft. Concretely, our Agents will take as input 
the environment object string such as "dirt" and "diamond" retrieved from Minecraft and output style specific synthetic texts related to 
the input, such as jokes and news headlines. 


## AI/ML Algorithms

We plan to explore various text to text generation algorithms such as seq2seq and transformers and decoding algorithms 
such as beam search and nucleus sampling.

## Evaluation Plan

#### quantitative evaluation

For quantitative evaluation, we plan to run our model with keyword to text validation data held out from training process and measure its performance with BLEU score and
PPLs. To ensure the generated text are style consistent, we plan to use pre-trained text classification models to predict the style label of
our synthetic texts, and we expect our generated snippets to be classified as the intented style. For relevance of model output to input keywords, we plan to explore word vector based/human scored approaches. Due to the lack of prior work in directly related task, we will develop our baselines as the project moves foward.

#### qualitative analysis

For qualitative evaluation, we plan to use human-centric evaluation methods to measure the generated text to the target style, a good literature review can be found [here](https://arxiv.org/abs/2006.14799). For sanity cases, we expected our output to display human-perceptible connection to its target style and input keywords. Meanwhile, although outputs from word level language generation models
are expected to suffer from degradation and will be somewhat noisy, we expect our generated text to be generally syntactically sound. We will monitor the logits produced by the
model in addition to generated text to check the internal behavior of the model.
In the moonshot case, we hope we could generate synthetic snippets that are indistinguishable from human written snippets to a human evaluator, and contains synonyms of/exact input keywords.

## Appointment

scheduled 10/21/2020, 9:30 am. 
