---
layout: default
title: Status
---


## Video

<iframe width="1120" height="630" src="https://youtu.be/WQxsgLZk0yg" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Project Summary

We propose Context Aware Language Generator for Minecraft(CALM), a framework for generating environment aware, style specific text snippets in Minecraft. Specifically, our agent will recognize the surrounding environment, which we refer to as context, to generate short stories that are coherent to the received environment. For example, given a river flowing near the agent as context and a user defined style such as horror story style, the agent should be able to generate short text snippets that contain string “river” in the style of horror stories.

Existing works on generating text with given string usually involves training customized model or changing the generation process to deviate from auto-regressive manner, thus making it not convenient to leverage these methods. On the other hand, modification-based methods that swapps the words into templates/existing texts fails to generate diverse samples, and the generated texts depends on its template. With these issues in mind, we propose to make use of pre-trained style-aware language model with our modified search-based decoding algorithm that ensures the output text contains the target string. We show our method could generate results that are style-coherent and sntactically-sound when compared to human-written texts, and does not require the user to train a customized model.

## Approaches

To achieve our goal of generating text that is coherent to the environment in Minecraft, our work involves the following two modules:

* A environment-perception module that returns string of nearby objects based on nearby blocks, mobs, and configurations in Malmo world XML file.

* A text generation module that generates a story snippet based on given strings produced by the environment-perception module. 

The rest of this section is organized as follows: we first cover the <b>background concepts related to our implementation</b>, then introduces both the <b>baseline and proposed version of language generation approach</b>. Finally, we introduce how we <b>retrieve string from the Malmo environment</b>.

### 1. Background

To make the report self-contained, we briefly cover the concept of language modeling, text generation, decoding methods, part-of-speech tagging and GPT-2 in this subsection. 

* <i>Language modeling: </i> The objective of language modeling is to learn the probability of a given sentence s and its words $$w_i$$, denoted as $$s=(w_0,w_1,...w_n)$$ with respect to some corpus. When using a neural network with set of parameters $$\theta$$ to conduct language modeling, the task is often formulated as a classifier that attempts to learn the true probability distribution of the next token given a series of previous words $$p_{\theta}(w_i \mid w_{<i}) \approx q(w_i \mid w_{<i})$$.


* <i>Text generation and decoding methods: </i> Losely speaking, text generation is achieved by incrementally generating the next word $$w_i$$ given $$w_{<i}$$, until an end of sentence token is sampled($$w_i = \textit{<EOS>}$$). However, various research have shown that greedy decoding algorithm that selects word that maximizes the conditional probability $$p(w_i \mid w_{<i})$$ is problematic, and imposes issues such as generated text becomes a sequence of same words.

    To address this issue, several methods such as beam search, top-k sampling and nucleus sampling have been developed, with the general idea of incorporating stochasticity into the generation process. Concretely, these algorithms will still choose a word $$w_i$$ with high probability at each step, but do not always choose the word that maximizes the conditional probability.
    
    
* <i>Part of speech tagging:</i> Part of speech tagging is the task of assigning part of speech to each word for a given sequence. Examples of POS tags are Nouns(NN), proper Nouns(NNP) and coordinating conjunctions(CC). There are multiple ways to achieve this task, such as neural network based methods and conditional random field based methods. Libraries that provides this functionality includes NLTK, StanfordNLP tagger, etc.


* <i>GPT-2: </i>The GPT-2 model is a [transformer](http://jalammar.github.io/illustrated-transformer/)-based model trained on 8-million web pages. The model could be used as-is, but could also be fine-tuned on domain specific text to adapt to tasks that require the model to understand things beyond web pages. For example, our work uses a GPT-2 model trained on stories. 

### 2. Text generation methods

We introduce the implementaion of our baseline and proposed approach, and discuss their advantages and disadvantages in this subsection.

#### 2.1 baseline generation approach

In comparison to our proposed generation method, we implemented a generator that swaps the target string into pre-stored human-written story snippets. Upon initialization, the generator keeps a pool of stories with genre labels. In the generation process, we first randomly sample a story snippet of desired style from the story pool, then swaps the given string into the sampled story. 

To determine the position to swap the target string in, we make use of [part-of-speech](https://medium.com/analytics-vidhya/pos-tagging-using-conditional-random-fields-92077e5eaa31#:~:text=POS%20tagging%20is%20the%20process,which%20the%20word%20is%20used.) labels. Specifically, we view a position in the sampled text as potential position if the part-of-speech tag of the original token at such position is the same as the desired string.

#### 2.2 proposed generation approach

![](src/decoding.png){:height="80%" width="80%"}

<i>our proposed approach</i>

We choose pretrained GPT-2 model fine tuned on style specific corpus such as horror story and super hero stories for language generation. At each language generation step, the pretrained model ouputs a logits of  corpus size that specifies the probability of the corresponding words to appear at the current position. Traditionally, the word chosen at each generation step is achived by approaches such as nucleus sampling and top-k sampling([see here](https://arxiv.org/pdf/1904.09751.pdf)). 

To achieve context aware langauge generation, our system retrieves description of surrounding blocks from adjacent blocks of the agent(such as 'diamond_block') and returns a string that is common in natural language('diamond'). We then try to make the target word appear in our output text snippet by finding a position where the target word is most likely to appear. Formally, the context aware language generation task is defined as finding a sequence $$(w_1,w_2,w_3... w_n)$$ with an victim word $$w_v$$ such that $$abs(p(target word \mid w_0, ... , w_{v-1})-p(w_v \mid w_0, ... , w_{v_1}))$$ is minimized, while the raw probability of a certain word is sampled at each generation step after the word swapping happened is given by $$p(w_i \mid w_0, w_1, ... , target word, ... , w_{i-1})$$(prior to applying topk/nucleus sampling). 

![](src/gptGen.png)
<i>a more detailed description</i>

To find the optimal sequence, our system generates candidate sequence by computing the potential target word swapping loss $$abs(p(target word \mid h_{t-1})-p(chosen word \mid h_{t-1}))$$ at each generation step t, and view the current sequence as a candidate hypothesis if such loss is smaller than a pre-defined threshhold. Upon generation of a hypothesis, the word swapping loss is assigned to that branch as a score. Meanwhile, the system will keep on the generation process with other possible cases where the word swap did not take place, untill a new position where the target word could be swapped in or end of generation steps is reached. After the exploration of candicate hypothesises is done, we choose the word sequence with lowest swapping loss as output.

### 3. Environment perception methods

We cover our method for retrieving strings from surrounding environment in this section. 

* <i>Detecting object from single block:</i> 

    We use ObservationFromGrid to detect the object from a single block. When present, the Mod will return observations that say what the nearby blocks are.

* <i>Detecting object from composite block:</i> 

    We use ObservationFromGrid to detect the object from a single block. When present, the Mod will return observations that say what the nearby blocks are and I use some if and else to determine the composite block. For example, if there are two or more leaves, it must be a tree.

* <i>Detecting mob:</i> 

    We use ObservationFromNearbyEntities to detect mobs. When present, the Mod will return observations that list the positions of all entities that fall within the given ranges of the agent. A JSON array will be returned for each range requested, named using the name attribute of the range. Within the array will be a series of elements, one for each entity


## Evaluation

| Style | Target word   | Word seed | Text |
| :---    | ---:   | ---:        | ---:  |
| drama | sword      | Long long ago | :::: Long long ago , the sword master Yutai became possessed of his magic talent, transforming from human-type sword into the "Seven Stars of the Jade Buddha" when the Buddha was destroyed by a group of assassins |
| horror | pig      | In the deep forest | :::: In the deep forest surrounding The Bahamas in 1964 a pig called Nino, a "ghost," awake with fear from a nightmare, has entered an experimental serum and now exists only by a mysterious fate |
| super hero | lava      | In the deep forest | :::: In the deep forest in Nevada, lava from above has erupted causing a series and unexpected geological collapses that destroy several surrounding communities while a small, humanoid creature called S.S. Spider, who can breathe flames that does |


To evaluate our proposed generation method, we compare results of our method against our baseline and/or human written short story snippets in various setups. We evaluate our results by the following characteristics:

* <i>Style coherency:</i> We expect our generated text to be coherent with the intended style, ideally as coherent as human-written texts. 

* <i>Syntactical soundess:</i> We expect our generated text is grammartically correct. 


We show our method could generate text that is generally on par with human written story snippets in terms of style and grammar. 


### 1. style coherent

To ensure the results we generated are style coherent, we choose to use human evaluation metrics to ensure the ouputs are indeed of the intended style. We use two methods to check this feature: letting human evaluators guess the style of a given text without knowing its genre, and letting human evaluators rate the style coherency of a text given its genre. In both settings, we evaluated our generated text against human written text snippets. Note that our swap-based generator uses samples from the same human written text dataset, thus we omit its results from this section in particular.

#### 1.1 measurement by style classification

Specifically, we randomly sample sentences with different styles from our system, and let human readers guess the genre of the generated sentence. Upon evaluation, the human rater is allowed to pick two genres out of the six possible genres. We mark a text snippet is correctly recognized if one of the guessed genre by human evaluator is the true genre of that text. We report the averaged recognized examples among human evaluators as follows:

| Method | Average correctly recognized samples | 
| :---    | ---:   | 
| Human Written | 37/60      | 
| CALM<i>(proposed)</i> |  35/60     |
| Random Selection |  20/60     |

Note that the Random Selection row is the result one would get if genre labels were randomly assigned to 60 samples with balancely distributed genres. Interestingly, upon evaluation we found that it is harder than expected for a human evaluator to guess the genre of a text snippets. In conclusion, we show that our  generated result could achieve similar performance as human-produced texts.


#### 1.1 measurement by score-based evaluation

We then let human evaluators rate the coherence score of a piece of text given its genre from 0 to 5. More precisely, 0 means not coherent at all and 5 means the genre is extremely clear. We show that our generated text generally achieves result as good as human written texts.

| Method | Average rated score (60 samples)| 
| :---    | ---:   | 
| Human Written | 3.75/5.0     | 
| CALM<i>(proposed)</i> |  3.67/5.0     |

### 2. syntactically sound

To ensure our method only impose minimal damage to the ability of language model to generate syntactically correct text, we use Grammarly, an open source grammar checker to check the suspected grammar errors in our generated text. For a given docment, grammarly will reports the count of suspected errors and an overall score for writting([description of grammarly score](https://support.grammarly.com/hc/en-us/articles/360007144751-What-is-Performance-and-how-is-it-calculated-)).

| Method | Error Count(120 samples)   | Grammarly Score |
| :---    | ---:   | ---:        |
| Swap-based<i>(baseline)</i> | 147      | 87 |
| Human Written | 142      | 86 | 
| CALM<i>(proposed)</i> | 151      | 85 | 


Specifically, we pasted 120 generated samples for both the proposed method, the baseline method and human written texts into grammarly. The number of flagged errors and overall writing scores is shown as above. We conclude that our proposed method could generate text that are as grammarly sound as humans.

In general, all methods of generation will generate grammartically correct text snippets, and the difference in error count and scores is within the tolerant level for compensating the stochasity of sampling. Note that grammarly assigns different weights for different errors, so a document with more errors could still get a higher overall score - the Grammarly Score should be treated more of a qualititive metric.


### 3. other qualitative discussions

A basic requirement for our language generation task is the ability to make the target string appear in the output. To evaluate this, we queried both our baseline generator and proposed generator for 120 samples, and both of the generators succeeded in all cases. 

## Resources Used

* [Hugging Face pretrained models](https://huggingface.co/)
* [NLTK](https://www.nltk.org/)
* [Grammar Checker in Python](https://pypi.org/project/grammar-check/)
* Grammarly
