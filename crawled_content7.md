# Top AI/LLM learning resource in 2025

URL: https://originshq.com/blog/top-ai-llm-learning-resource-in-2025/#ib-toc-anchor-0

Crawled at: 2025-02-28T11:21:42.850369

## Summary

The blog is divided into three main segments:

1. **LLM Fundamentals (optional)**:
   - Covers essential topics like mathematics, Python, and neural networks.
   - Key areas include linear algebra, calculus, probability and statistics, Python basics, data science libraries, data preprocessing, machine learning libraries, and neural network fundamentals.

2. **The LLM Scientist**:
   - Focuses on creating high-performing LLMs using state-of-the-art techniques.
   - Key areas include LLM architecture, pre-training models, post-training datasets, supervised fine-tuning, preference alignment, evaluation, quantization, and new trends.

3. **The LLM Engineer**:
   - Emphasizes building and deploying applications based on LLMs.
   - Key areas include running LLMs, building vector storage, retrieval augmented generation, advanced RAG, inference optimization, deploying LLMs, and securing LLMs.

Additional sections include notebooks, tools, fine-tuning, quantization, and other related topics.



The Blog is organized into three main segments:



- LLM Fundamentals(optional) – Covers essential topics such as mathematics, Python, and neural networks.

- The LLM Scientist– Concentrates on creating the best-performing LLMs using state-of-the-art techniques.

- The LLM Engineer– Focuses on building applications based on LLMs and deploying them.





### 📝 Notebooks



Below is a collection of notebooks and articles dedicated to LLMs.



### Tools





### Fine-tuning





### Quantization





### Other







### LLM Fundamentals



This section provides core knowledge about mathematics, Python, and neural networks. While you may not begin here if you already have the basics, feel free to refer back as needed.



### 1. Mathematics for Machine Learning



Before diving deep into machine learning, it is essential to master the fundamental mathematical concepts that underpin these algorithms:



- Linear Algebra: Crucial for many algorithms, particularly in deep learning. Topics include vectors, matrices, determinants, eigenvalues and eigenvectors, vector spaces, and linear transformations.

- Calculus: Needed to optimize continuous functions. Learn about derivatives, integrals, limits, series, multivariable calculus, and gradient concepts.

- Probability and Statistics: Key for understanding model behavior and data prediction. Essential topics include probability theory, random variables, distributions, expectations, variance, covariance, correlation, hypothesis testing, confidence intervals, maximum likelihood estimation, and Bayesian inference.



Resources:



- 3Blue1Brown – The Essence of Linear Algebra

- StatQuest with Josh Starmer – Statistics Fundamentals

- AP Statistics Intuition by Ms Aerin

- Immersive Linear Algebra

- Khan Academy – Linear Algebra

- Khan Academy – Calculus

- Khan Academy – Probability and Statistics





### 2. Python for Machine Learning



Python is a flexible and powerful language, especially suited for machine learning because of its clear syntax and extensive ecosystem.



- Python Basics: Understand basic syntax, data types, error handling, and object-oriented programming.

- Data Science Libraries: Gain experience with NumPy for numerical operations; Pandas for data manipulation; and Matplotlib/Seaborn for visualizations.

- Data Preprocessing: Learn techniques such as feature scaling, normalization, handling missing values, outlier detection, encoding categorical data, and data splitting.

- Machine Learning Libraries: Familiarize yourself with Scikit-learn, which offers numerous supervised and unsupervised algorithms. Understand implementations of linear regression, logistic regression, decision trees, random forests, k-nearest neighbors, K-means clustering, and dimensionality reduction methods like PCA and t-SNE.



Resources:



- Real Python

- freeCodeCamp – Learn Python

- Python Data Science Handbook

- freeCodeCamp – Machine Learning for Everybody

- Udacity – Intro to Machine Learning





### 3. Neural Networks



Neural networks form the backbone of many modern deep learning models. It’s important to understand how they work and are built:



- Fundamentals: Know the basic structure including layers, weights, biases, and activation functions (sigmoid, tanh, ReLU, etc.).

- Training and Optimization: Get to know backpropagation, common loss functions (MSE, Cross-Entropy), and optimization algorithms (Gradient Descent, SGD, RMSprop, Adam).

- Overfitting: Understand what overfitting means and study regularization techniques such as dropout, L1/L2 regularization, early stopping, and data augmentation.

- Implementing a Multilayer Perceptron (MLP): Build an MLP (a fully connected network) using frameworks like PyTorch.



Resources:



- 3Blue1Brown – But what is a Neural Network?

- freeCodeCamp – Deep Learning Crash Course

- Fast.ai – Practical Deep Learning

- Patrick Loeber – PyTorch Tutorials





### 4. Natural Language Processing (NLP)



NLP is an exciting field that connects human language with machine comprehension. It ranges from basic text processing to capturing intricate linguistic nuances.



- Text Preprocessing: Understand tokenization (dividing text into words or sentences), stemming (reducing words to their roots), lemmatization (context-aware reduction), and stop word removal.

- Feature Extraction Techniques: Learn how to transform textual data for machine learning algorithms using techniques like Bag-of-Words (BoW), TF-IDF, and n-grams.

- Word Embeddings: Study methods such as Word2Vec, GloVe, and FastText which allow words with similar meanings to have similar vector representations.

- Recurrent Neural Networks (RNNs): Learn how RNNs are designed for sequential data and explore variants like LSTMs and GRUs, which capture long-term dependencies.



Resources:



- Lena Voita – Word Embeddings

- RealPython – NLP with spaCy in Python

- Kaggle – NLP Guide

- Jay Alammar – The Illustration Word2Vec

- Jake Tae – PyTorch RNN from Scratch

- colah’s blog – Understanding LSTM Networks





### The LLM Scientist



This section is designed to help you learn how to build the most effective LLMs using the latest methodologies.



### 1. The LLM Architecture



You don’t need an exhaustive understanding of the Transformer architecture, but it is important to know the major steps in modern LLMs: converting text into numeric tokens, processing these tokens with layers (including attention mechanisms), and using various sampling strategies to generate text.



- Architectural Overview: Trace the evolution from encoder-decoder Transformers to decoder-only structures like GPT, which are fundamental to modern LLMs. Understand how these models process and generate text at a high level.

- Tokenization: Learn the principles behind tokenization and how it transforms text into numerical data that models can process. Investigate different tokenization strategies and their effects on performance and output quality.

- Attention Mechanisms: Master the concept of attention, particularly self-attention and its variants, and see how they help models deal with long-range dependencies and maintain contextual integrity.

- Sampling Techniques: Compare deterministic methods (e.g., greedy search, beam search) to probabilistic methods (e.g., temperature sampling, nucleus sampling) and evaluate the trade-offs involved.



References:



- Visual intro to Transformersby 3Blue1Brown

- LLM Visualizationby Brendan Bycroft

- nanoGPTby Andrej Karpathy (includes a tokenization video:here)

- Attention? Attention!by Lilian Weng

- Decoding Strategies in LLMsby Maxime Labonne





### 2. Pre-training Models



Pre-training LLMs is an expensive and resource-intensive process. Although this course does not primarily focus on pre-training, understanding the process, particularly regarding data handling and model parameters, is crucial. For smaller-scale hobbyist projects, pre-training on models with fewer than 1B parameters is feasible.



- Data Preparation: Pre-training requires vast datasets (for example,Llama 3.1was trained on 15 trillion tokens), which must be curated, cleaned, deduplicated, and tokenized. Modern pipelines include extensive quality filtering.

- Distributed Training: Explore techniques such as data parallelism (distributing batches), pipeline parallelism (distributing layers), and tensor parallelism (splitting operations). These require effective network communication and memory management across GPU clusters.

- Training Optimization: Utilize adaptive learning rate schedules with warm-up, gradient clipping and normalization, mixed-precision training, and modern optimizers (AdamW, Lion) with well-tuned hyperparameters.

- Monitoring: Implement dashboards and logging to track metrics (loss, gradients, GPU usage) and profile performance to identify computational and communication bottlenecks.



References:



- FineWebby Penedo et al.

- RedPajama v2by Weber et al.

- nanotronby Hugging Face (used forSmolLM2)

- Parallel Trainingby Chenyan Xiong

- Distributed Trainingby Duan et al.

- OLMo 2by AI2

- LLM360by LLM360





### 3. Post-training Datasets



Post-training datasets are organized with clear structures including instructions paired with answers (supervised fine-tuning) or instructions paired with chosen/rejected responses (preference alignment). Given that conversational datasets are less common compared to raw pre-training data, additional processing is often needed to enhance sample accuracy, diversity, and complexity. More details can be found in the💾 LLM Datasetsrepository.



- Storage & Chat Templates: Due to their conversational nature, these datasets are stored in formats such as ShareGPT or OpenAI/HF. These are then mapped to chat templates like ChatML or Alpaca for training.

- Synthetic Data Generation: Use frontier models like GPT-4o to create instruction-response pairs from seed data. This method offers flexibility and scalability, with considerations for diverse seed tasks and effective system prompts.

- Data Enhancement: Enhance your samples with techniques including verified outputs (using unit tests/solvers), generating multiple answers with rejection sampling,Auto-Evol, Chain-of-Thought, Branch-Solve-Merge, persona-based approaches, and more.

- Quality Filtering: Traditional filtering methods involve rule-based approaches, duplicate removal (using MinHash or embeddings), and n-gram decontamination, with reward models and judge LLMs providing additional quality control.



References:



- Synthetic Data Generatorby Argilla

- LLM Datasetsby Maxime Labonne

- NeMo-Curatorby Nvidia

- Distilabelby Argilla

- Semhashby MinishLab

- Chat Templateby Hugging Face





### 4. Supervised Fine-Tuning



Supervised Fine-Tuning (SFT) transforms base models into helpful assistants capable of following instructions and structuring answers effectively. Although SFT can be used to introduce new knowledge, its ability to completely learn a new language is limited. Thus, prioritizing data quality over parameter tuning is essential.



- Training Techniques: Full fine-tuning updates all parameters but requires significant computational resources. Techniques like LoRA and QLoRA update only a small number of adapter parameters while keeping the base model frozen. QLoRA further combines 4-bit quantization with LoRA to minimize VRAM usage.

- Training Parameters: Important parameters to manage include the learning rate (with schedulers), batch size, gradient accumulation, number of epochs, optimizers (e.g., 8-bit AdamW), weight decay, warmup steps, and specific LoRA parameters (rank, alpha, target modules).

- Distributed Training: Utilize multiple GPUs via frameworks such as DeepSpeed or FSDP. DeepSpeed offers ZeRO optimization stages to improve memory efficiency by partitioning state information. Both frameworks support gradient checkpointing.

- Monitoring: Keep an eye on metrics like loss curves, learning rate changes, and gradient norms, while addressing issues such as loss spikes or gradient explosions.



References:



- Fine-tune Llama 3.1 Ultra-Efficiently with Unslothby Maxime Labonne

- Axolotl – Documentationby Wing Lian

- Mastering LLMsby Hamel Husain

- LoRA insightsby Sebastian Raschka





### 5. Preference Alignment



Preference alignment is a secondary stage in the post-training process that helps fine-tune the model’s tone and reduce issues like toxicity and hallucinations. Its purpose is to improve performance and usefulness, and it generally involves methods like Direct Preference Optimization (DPO) and Proximal Policy Optimization (PPO).



- Rejection Sampling: For each prompt, generate multiple responses from the model, then score them to create on-policy data consisting of both chosen and rejected answers.

- Direct Preference Optimization: This method optimizes the policy by directly increasing the likelihood of chosen responses over rejected ones, without needing a separate reward model. Although it is more computationally efficient than PPO, it may offer a slight decrease in quality.

- Proximal Policy Optimization: This method iteratively updates the policy to maximize rewards while keeping changes close to the original behavior, using a reward model to score responses and requiring careful hyperparameter tuning (learning rate, batch size, and PPO clip range).

- Monitoring: Alongside SFT metrics, monitor the margin between chosen and rejected responses and track overall accuracy improvements until reaching a plateau.



References:



- Illustrating RLHFby Hugging Face

- LLM Training: RLHF and Its Alternativesby Sebastian Raschka

- Preference Tuning LLMsby Hugging Face

- Fine-tune Mistral-7b with DPOby Maxime Labonne

- DPO Wandb logsby Alexander Vishnevskiy





### 6. Evaluation



Evaluating LLMs reliably is a challenging but essential task for refining dataset composition and training settings. It is important to acknowledge Goodhart’s law: “When a measure becomes a target, it ceases to be a good measure.”



- Automated Benchmarks: Use curated datasets and metrics (such as MMLU) to assess performance on specific tasks. This approach works well for concrete tasks but may struggle with abstract capabilities and suffer from data contamination.

- Human Evaluation: Involve human assessors to prompt models and rate outputs. This method ranges from informal checks to systematic annotations and large-scale community voting (arena) and tends to work best for subjective assessments.

- Model-based Evaluation: Implement judge or reward models to assess generated responses. Although they often correlate well with human judgment, these models may be biased toward their own outputs.

- Feedback Signal: Analyze error patterns to identify shortcomings, such as problems following complex instructions, lacking specific knowledge, or being vulnerable to adversarial prompts. Use the feedback to adjust data generation and training parameters.



References:



- Evaluation Guidebookby Clémentine Fourrier

- Open LLM Leaderboardby Hugging Face

- Language Model Evaluation Harnessby EleutherAI

- Lightevalby Hugging Face

- Chatbot Arenaby LMSYS





### 7. Quantization



Quantization converts a model’s parameters and activations from high precision (e.g., FP32) to lower precision (such as 4 bits) to reduce compute and memory requirements.



- Base Techniques: Understand the different precisions (FP32, FP16, INT8, etc.) and basic quantization methods like absmax and zero-point techniques.

- GGUF & llama.cpp: Originally created for CPU-based runs,llama.cppand the GGUF format are now widely used to run LLMs on consumer hardware. They support the storage of special tokens, vocabulary, and metadata all in one file.

- GPTQ & AWQ: Methods such asGPTQ/EXL2andAWQuse layer-wise calibration to maintain performance at very low bitwidths. These techniques adjust scaling dynamically and can selectively bypass or re-center the heaviest parameters.

- SmoothQuant & ZeroQuant: New methods such as SmoothQuant (which applies quantization-friendly transformations) and compiler-based optimizations like ZeroQuant help alleviate outlier issues before quantization, optimizing data flow and reducing hardware overhead.



References:



- Introduction to Quantizationby Maxime Labonne

- Quantize Llama models with llama.cppby Maxime Labonne

- 4-bit LLM Quantization with GPTQby Maxime Labonne

- Understanding Activation-Aware Weight Quantizationby FriendliAI

- SmoothQuant on Llama 2 7Bby MIT HAN Lab

- DeepSpeed Model Compressionby DeepSpeed





### 8. New Trends



This section covers emerging topics that do not neatly fit into other categories. Some ideas, like model merging and multimodal models, are well established, while others—such as interpretability or test-time compute scaling—are more experimental and actively researched.



- Model Merging: Merging pre-trained models has become a popular technique for boosting performance without additional fine-tuning. Themergekitlibrary implements several popular merging methods, including SLERP,DARE, andTIES.

- Multimodal Models: Models likeCLIP,Stable Diffusion, andLLaVAare designed to process and integrate various types of inputs (text, images, audio, etc.) within a unified embedding space, enabling powerful applications such as text-to-image generation.

- Interpretability: Mechanistic interpretability approaches, including Sparse Autoencoders (SAEs) and techniques like abliteration, offer insights into the internal operations of LLMs and can allow for behavioral adjustments without retraining.

- Test-time Compute: Scaling computational resources during inference often requires multiple calls and specialized models (e.g., Process Reward Model (PRM)). Iterative procedures with fine-tuned scoring can markedly enhance performance on complex reasoning tasks.



References:



- Merge LLMs with mergekitby Maxime Labonne

- Smol Visionby Merve Noyan

- Large Multimodal Modelsby Chip Huyen

- Uncensor any LLM with abliterationby Maxime Labonne

- Intuitive Explanation of SAEsby Adam Karvonen

- Scaling test-time computeby Beeching et al.





### The LLM Engineer



This part of the course teaches you how to build production-grade applications powered by LLMs, with a focus on augmenting models and deploying them.



### 1. Running LLMs



Running LLMs can be challenging given their high hardware requirements. Depending on your needs, you might opt to use an API (like GPT-4) or run a model locally. In either case, careful prompting and guidance can greatly enhance output quality and relevance.



- LLM APIs: APIs provide a convenient way to access LLMs. They are divided between private LLMs (e.g.,OpenAI,Google,Anthropic,Cohere) and open-source LLMs (e.g.,OpenRouter,Hugging Face,Together AI).

- Open-source LLMs: TheHugging Face Hubis a prime resource for finding LLMs. You can run many of these models inHugging Face Spaces, or download and operate them locally using tools likeLM Studio,llama.cpp, orOllama.

- Prompt Engineering: Techniques such as zero-shot prompting, few-shot prompting, chain-of-thought, and ReAct are common. While these methods work better with larger models, they can be adapted for smaller ones.

- Structuring Outputs: Some tasks require outputs to follow a strict format (such as a JSON format or specific template). Tools such asLMQL,Outlines, andGuidancehelp ensure the generated text adheres to the required structure.



References:



- Run an LLM locally with LM Studioby Nisha Arya

- Prompt engineering guideby DAIR.AI

- Outlines – Quickstart

- LMQL – Overview





### 2. Building a Vector Storage



The first step in creating a Retrieval Augmented Generation (RAG) pipeline is establishing a vector storage. This involves loading documents, splitting them into manageable pieces, and then converting key text chunks into vector embeddings for future retrieval.



- Ingesting Documents: Document loaders can process multiple formats such as PDF, JSON, HTML, and Markdown. They can also pull in data directly from databases and APIs (e.g., GitHub, Reddit, Google Drive).

- Splitting Documents: Text splitters divide documents into smaller, semantically relevant chunks. Instead of a fixed character count, splitting by headers or recursively—while preserving metadata—often yields better results.

- Embedding Models: These models transform text into vector representations, enabling a more nuanced semantic interpretation that is essential for effective search.

- Vector Databases: Databases likeChroma,Pinecone,Milvus,FAISS, andAnnoyare designed for storing embeddings, allowing for fast similarity-based retrieval.



References:



- LangChain – Text splitters

- Sentence Transformers library

- MTEB Leaderboard

- The Top 5 Vector Databasesby Moez Ali





### 3. Retrieval Augmented Generation



Retrieval Augmented Generation (RAG) enhances LLM outputs by using relevant contextual documents fetched from a vector database, thus improving answer accuracy without needing additional fine-tuning.



- Orchestrators: Tools likeLangChain,LlamaIndex, andFastRAGconnect LLMs to tools, databases, and memory systems, extending their functionality.

- Retrievers: Since user queries may not be optimized for search, techniques such as multi-query retrievers orHyDEcan reformulate queries to improve retrieval performance.

- Memory: To maintain context over a conversation, LLMs use a history buffer that can be enhanced with summarization techniques or integrated with vector stores via RAG.

- Evaluation: It is crucial to assess both the document retrieval process (precision and recall) and the generation stage (faithfulness and relevancy). Tools likeRagasandDeepEvalcan assist in these evaluations.



References:



- Llamaindex – High-level concepts

- Pinecone – Retrieval Augmentation

- LangChain – Q&A with RAG

- LangChain – Memory types

- RAG pipeline – Metrics





### 4. Advanced RAG



In real-world scenarios, you may need to develop more complex pipelines involving SQL or graph databases, as well as systems that automatically select appropriate tools and APIs to enhance the baseline RAG setup.



- Query Construction: For structured data stored in databases, you need to translate user instructions into appropriate query languages like SQL or Cypher.

- Agents and Tools: LLM agents can automatically choose the most suitable tools—ranging from simple web searches (e.g., Google, Wikipedia) to complex systems (e.g., Python interpreters, Jira)—to answer queries.

- Post-Processing: Enhance the overall relevance of retrieved documents using re-ranking methods,RAG-fusion, or classification techniques.

- Program LLMs: Frameworks likeDSPyallow you to fine-tune prompts and model parameters programmatically based on automated evaluations.



References:



- LangChain – Query Construction

- LangChain – SQL

- Pinecone – LLM agents

- LLM Powered Autonomous Agentsby Lilian Weng

- LangChain – OpenAI’s RAG

- DSPy in 8 Steps





### 5. Inference Optimization



Since generating text is computationally intensive, several techniques exist to maximize throughput and reduce inference costs alongside quantization.



- Flash Attention: Optimizes the attention mechanism by reducing its complexity from quadratic to linear, thereby speeding up both training and inference.

- Key-value Cache: Learn about the key-value cache and enhancements likeMulti-Query Attention(MQA) andGrouped-Query Attention(GQA).

- Speculative Decoding: Use a smaller model to produce draft outputs that are later refined by a larger model, thus accelerating text generation.



References:



- GPU Inferenceby Hugging Face

- LLM Inferenceby Databricks

- Optimizing LLMs for Speed and Memoryby Hugging Face

- Assisted Generationby Hugging Face





### 6. Deploying LLMs



Deploying LLMs, especially at scale, is complex and may require multiple GPU clusters. However, demos or local applications often have simpler requirements.



- Local Deployment: Open-source LLMs offer privacy advantages over private models. Solutions such asLM Studio,Ollama,oobabooga, andkobold.cppfacilitate local deployment.

- Demo Deployment: Tools likeGradioandStreamlitare excellent for prototyping apps and sharing demos. They are also easy to host online (for example, onHugging Face Spaces).

- Server Deployment: Running LLMs at scale often demands cloud infrastructure (or on-prem solutions) and specialized frameworks such asTGIorvLLM.

- Edge Deployment: In resource-constrained environments, frameworks likeMLC LLMandmnn-llmenable deployment on web browsers, Android, and iOS.



References:



- Streamlit – Build a basic LLM appby Streamlit

- HF LLM Inference Containerby Hugging Face

- Philschmid blogby Philipp Schmid

- Optimizing Latencyby Hamel Husain





### 7. Securing LLMs



LLM applications bring their own unique security challenges in addition to standard software vulnerabilities.



- Prompt Hacking: This includes issues like prompt injection (where unwanted instructions hijack the model), data/prompt leaking (extracting the original prompt or training data), and jailbreaking (bypassing the model’s safety features).

- Backdoors: These attacks can target training data by poisoning it with false or malicious content, or by introducing hidden triggers that alter model behavior during inference.

- Defensive Measures: Protect your LLM applications by testing them for vulnerabilities using techniques such as red teaming and tools likegarak, while monitoring in production with frameworks likelangfuse.



References:



- OWASP LLM Top 10by HEGO Wiki

- Prompt Injection Primerby Joseph Thacker

- LLM Securityby@llm_sec

- Red teaming LLMsby Microsoft



