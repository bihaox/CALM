---
layout: default
title: Proposal
---
## Project Summary

We consider the problem of generating environment aware, style specific text snipps in Minecraft. Concretely, our Agents will take as input 
the environment object string such as "dirt" and "diamond" retrieved from Minecraft and output style specific synthetic texts related to 
the input, such as jokes and news headlines. 


## AI/ML Algorithms

We plan to explore various text to text generation algorithms such as seq2seq and transformers and decoding algorithms 
such as beam search and nucleus sampling.

## Evaluation Plan

#### quantitative evaluation

For quantitative evaluation, we plan to run our model with keyword to text validation data held out from training process and measure its performance with BLEU score and
PPLs. To ensure the generated text are style consistent, we plan to use pre-trained text classification models to predict the style label of
our synthetic texts, and we expect our generated snippets to be classified as intented styles. Due to the lack of prior work in directly related
task, we will develop our baselines along the project.

#### qualitative analysis

For qualitative evaluation, we plan to use human-centric evaluation methods to measure the generated text to the target style. For sanity cases,
we expected our output to display human-perceptible connection to its target style and input keywords. In the moonshot case, we hope we could generate
synthetic snippets that are indistinguishable from human written snippets to a human evaluator. 

## Appointment
