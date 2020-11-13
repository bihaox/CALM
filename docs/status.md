---
layout: default
title: Status
---

## Project Summary

We consider the problem of generating environment aware, style specific text snippets in Minecraft. Concretely, our agent will take as input 
the environment object string such as "dirt" and "diamond" retrieved from Minecraft and output style specific synthetic texts related to 
the input, such as horror stories and super hero stories. 


## Approach

We choose pretrained GPT-2 model fine tuned on style specific corpus such as horror story and super hero stories for language generation. The decoding algorithm is currently
implemented as modified top-k sampling to make sure the input word appears in the output story. At each language generation step t, the pretrained model ouputs a categorical distribution of corpus size that specifies the likelihood of the corresponding word to appear at the current position. Formally, the original top-k sampling attempts to choose only from words with high likelihood by selecting from a subset of words that maximizes their cummulative probability([see here](https://arxiv.org/pdf/1904.09751.pdf)). 

To achieve context aware langauge generation, our system retrieved description of surrounding blocks from adjacent blocks to the agent(such as 'diamond_ore') and returns a string that is common in natural language('diamond'). We adopt this approach by implicitly investigating all of the k hypothesis, with the objective of finding the optimum position to force the target word appear in the output by minimizing the word swapping loss P\(true selected word|h\) - P\(targert word|h\) in the given generation steps. 

## Evaluation

## Remaining Goals and Challenges

We plan to improve our system by both improving our generation algorithm and the ease-of-use of the system. In the following periods, we plan to change our current usage of top-k sampling to nucleus sampling to enhance the naturalness of our generated text. Meanwhile, the current system lacks the ability to deal with composite blocks in the environment, for example, the system cannot retrieve the word "tree" from the environment as trees are represented in Minecraft as the composition of wood blocks and leaf blocks. Finally, we plan to augment our language generation process by using existing ontologies such as wordnet to construct more candidate target words(for example, given pigs, hogs could also be a candidate word) to encourage more variants in our ouput.

## Resources Used

* [Hugging Face pretrained models](https://huggingface.co/)
* [NLTK](https://www.nltk.org/)
* [Grammar Checker in Python](https://pypi.org/project/grammar-check/)
