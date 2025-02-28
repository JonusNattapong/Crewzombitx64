# Top AI/LLM learning resource in 2025

URL: https://originshq.com/blog/top-ai-llm-learning-resource-in-2025/#ib-toc-anchor-0

Crawled at: 2025-02-28T10:04:53.877168

The Blog is organized into three main segments:

1. LLM Fundamentals (optional) – Covers essential topics such as mathematics, Python, and neural networks.
2. The LLM Scientist – Concentrates on creating the best-performing LLMs using state-of-the-art techniques.
3. The LLM Engineer – Focuses on building applications based on LLMs and deploying them.

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

* Linear Algebra: Crucial for many algorithms, particularly in deep learning. Topics include vectors, matrices, determinants, eigenvalues and eigenvectors, vector spaces, and linear transformations.
* Calculus: Needed to optimize continuous functions. Learn about derivatives, integrals, limits, series, multivariable calculus, and gradient concepts.
* Probability and Statistics: Key for understanding model behavior and data prediction. Essential topics include probability theory, random variables, distributions, expectations, variance, covariance, correlation, hypothesis testing, confidence intervals, maximum likelihood estimation, and Bayesian inference.

Resources:

* [3Blue1Brown – The Essence of Linear Algebra](https://www.youtube.com/watch?v=fNk_zzaMoSs&list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab)
* [StatQuest with Josh Starmer – Statistics Fundamentals](https://www.youtube.com/watch?v=qBigTkBLU6g&list=PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9)
* [AP Statistics Intuition by Ms Aerin](https://automata88.medium.com/list/cacc224d5e7d)
* [Immersive Linear Algebra](https://immersivemath.com/ila/learnmore.html)
* [Khan Academy – Linear Algebra](https://www.khanacademy.org/math/linear-algebra)
* [Khan Academy – Calculus](https://www.khanacademy.org/math/calculus-1)
* [Khan Academy – Probability and Statistics](https://www.khanacademy.org/math/statistics-probability)

### 2. Python for Machine Learning

Python is a flexible and powerful language, especially suited for machine learning because of its clear syntax and extensive ecosystem.

* Python Basics: Understand basic syntax, data types, error handling, and object-oriented programming.
* Data Science Libraries: Gain experience with NumPy for numerical operations; Pandas for data manipulation; and Matplotlib/Seaborn for visualizations.
* Data Preprocessing: Learn techniques such as feature scaling, normalization, handling missing values, outlier detection, encoding categorical data, and data splitting.
* Machine Learning Libraries: Familiarize yourself with Scikit-learn, which offers numerous supervised and unsupervised algorithms. Understand implementations of linear regression, logistic regression, decision trees, random forests, k-nearest neighbors, K-means clustering, and dimensionality reduction methods like PCA and t-SNE.

Resources:

* [Real Python](https://realpython.com/)
* [freeCodeCamp – Learn Python](https://www.youtube.com/watch?v=rfscVS0vtbw)
* [Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/)
* [freeCodeCamp – Machine Learning for Everybody](https://youtu.be/i_LwzRVP7bg)
* [Udacity – Intro to Machine Learning](https://www.udacity.com/course/intro-to-machine-learning--ud120)

### 3. Neural Networks

Neural networks form the backbone of many modern deep learning models. It’s important to understand how they work and are built:

* Fundamentals: Know the basic structure including layers, weights, biases, and activation functions (sigmoid, tanh, ReLU, etc.).
* Training and Optimization: Get to know backpropagation, common loss functions (MSE, Cross-Entropy), and optimization algorithms (Gradient Descent, SGD, RMSprop, Adam).
* Overfitting: Understand what overfitting means and study regularization techniques such as dropout, L1/L2 regularization, early stopping, and data augmentation.
* Implementing a Multilayer Perceptron (MLP): Build an MLP (a fully connected network) using frameworks like PyTorch.

Resources:

* [3Blue1Brown – But what is a Neural Network?](https://www.youtube.com/watch?v=aircAruvnKk)
* [freeCodeCamp – Deep Learning Crash Course](https://www.youtube.com/watch?v=VyWAvY2CF9c)
* [Fast.ai – Practical Deep Learning](https://course.fast.ai/)
* [Patrick Loeber – PyTorch Tutorials](https://www.youtube.com/playlist?list=PLqnslRFeH2UrcDBWF5mfPGpqQDSta6VK4)

### 4. Natural Language Processing (NLP)

NLP is an exciting field that connects human language with machine comprehension. It ranges from basic text processing to capturing intricate linguistic nuances.

* Text Preprocessing: Understand tokenization (dividing text into words or sentences), stemming (reducing words to their roots), lemmatization (context-aware reduction), and stop word removal.
* Feature Extraction Techniques: Learn how to transform textual data for machine learning algorithms using techniques like Bag-of-Words (BoW), TF-IDF, and n-grams.
* Word Embeddings: Study methods such as Word2Vec, GloVe, and FastText which allow words with similar meanings to have similar vector representations.
* Recurrent Neural Networks (RNNs): Learn how RNNs are designed for sequential data and explore variants like LSTMs and GRUs, which capture long-term dependencies.

Resources:

* [Lena Voita – Word Embeddings](https://lena-voita.github.io/nlp_course/word_embeddings.html)
* [RealPython – NLP with spaCy in Python](https://realpython.com/natural-language-processing-spacy-python/)
* [Kaggle – NLP Guide](https://www.kaggle.com/learn-guide/natural-language-processing)
* [Jay Alammar – The Illustration Word2Vec](https://jalammar.github.io/illustrated-word2vec/)
* [Jake Tae – PyTorch RNN from Scratch](https://jaketae.github.io/study/pytorch-rnn/)
* [colah’s blog – Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)

### The LLM Scientist

This section is designed to help you learn how to build the most effective LLMs using the latest methodologies.

### 1. The LLM Architecture

You don’t need an exhaustive understanding of the Transformer architecture, but it is important to know the major steps in modern LLMs: converting text into numeric tokens, processing these tokens with layers (including attention mechanisms), and using various sampling strategies to generate text.

* Architectural Overview: Trace the evolution from encoder-decoder Transformers to decoder-only structures like GPT, which are fundamental to modern LLMs. Understand how these models process and generate text at a high level.
* Tokenization: Learn the principles behind tokenization and how it transforms text into numerical data that models can process. Investigate different tokenization strategies and their effects on performance and output quality.
* Attention Mechanisms: Master the concept of attention, particularly self-attention and its variants, and see how they help models deal with long-range dependencies and maintain contextual integrity.
* Sampling Techniques: Compare deterministic methods (e.g., greedy search, beam search) to probabilistic methods (e.g., temperature sampling, nucleus sampling) and evaluate the trade-offs involved.

References:

* [Visual intro to Transformers](https://www.youtube.com/watch?v=wjZofJX0v4M) by 3Blue1Brown
* [LLM Visualization](https://bbycroft.net/llm) by Brendan Bycroft
* [nanoGPT](https://www.youtube.com/watch?v=kCc8FmEb1nY) by Andrej Karpathy (includes a tokenization video: [here](https://www.youtube.com/watch?v=zduSFxRajkE))
* [Attention? Attention!](https://lilianweng.github.io/posts/2018-06-24-attention/) by Lilian Weng
* [Decoding Strategies in LLMs](https://mlabonne.github.io/blog/posts/2023-06-07-Decoding_strategies.html) by Maxime Labonne

### 2. Pre-training Models

Pre-training LLMs is an expensive and resource-intensive process. Although this course does not primarily focus on pre-training, understanding the process, particularly regarding data handling and model parameters, is crucial. For smaller-scale hobbyist projects, pre-training on models with fewer than 1B parameters is feasible.

* Data Preparation: Pre-training requires vast datasets (for example, [Llama 3.1](https://arxiv.org/abs/2307.09288) was trained on 15 trillion tokens), which must be curated, cleaned, deduplicated, and tokenized. Modern pipelines include extensive quality filtering.
* Distributed Training: Explore techniques such as data parallelism (distributing batches), pipeline parallelism (distributing layers), and tensor parallelism (splitting operations). These require effective network communication and memory management across GPU clusters.
* Training Optimization: Utilize adaptive learning rate schedules with warm-up, gradient clipping and normalization, mixed-precision training, and modern optimizers (AdamW, Lion) with well-tuned hyperparameters.
* Monitoring: Implement dashboards and logging to track metrics (loss, gradients, GPU usage) and profile performance to identify computational and communication bottlenecks.

References:

* [FineWeb](https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-v1) by Penedo et al.
* [RedPajama v2](https://www.together.ai/blog/redpajama-data-v2) by Weber et al.
* [nanotron](https://github.com/huggingface/nanotron) by Hugging Face (used for [SmolLM2](https://github.com/huggingface/smollm))
* [Parallel Training](https://www.andrew.cmu.edu/course/11-667/lectures/W10L2%20Scaling%20Up%20Parallel%20Training.pdf) by Chenyan Xiong
* [Distributed Training](https://arxiv.org/abs/2407.20018) by Duan et al.
* [OLMo 2](https://allenai.org/olmo) by AI2
* [LLM360](https://www.llm360.ai/) by LLM360

### 3. Post-training Datasets

Post-training datasets are organized with clear structures including instructions paired with answers (supervised fine-tuning) or instructions paired with chosen/rejected responses (preference alignment). Given that conversational datasets are less common compared to raw pre-training data, additional processing is often needed to enhance sample accuracy, diversity, and complexity. More details can be found in the [💾 LLM Datasets](https://github.com/mlabonne/llm-datasets) repository.

* Storage & Chat Templates: Due to their conversational nature, these datasets are stored in formats such as ShareGPT or OpenAI/HF. These are then mapped to chat templates like ChatML or Alpaca for training.
* Synthetic Data Generation: Use frontier models like GPT-4o to create instruction-response pairs from seed data. This method offers flexibility and scalability, with considerations for diverse seed tasks and effective system prompts.
* Data Enhancement: Enhance your samples with techniques including verified outputs (using unit tests/solvers), generating multiple answers with rejection sampling, [Auto-Evol](https://arxiv.org/abs/2406.00770), Chain-of-Thought, Branch-Solve-Merge, persona-based approaches, and more.
* Quality Filtering: Traditional filtering methods involve rule-based approaches, duplicate removal (using MinHash or embeddings), and n-gram decontamination, with reward models and judge LLMs providing additional quality control.

References:

* [Synthetic Data Generator](https://huggingface.co/spaces/argilla/synthetic-data-generator) by Argilla
* [LLM Datasets](https://github.com/mlabonne/llm-datasets) by Maxime Labonne
* [NeMo-Curator](https://github.com/NVIDIA/NeMo-Curator) by Nvidia
* [Distilabel](https://distilabel.argilla.io/dev/sections/pipeline_samples/) by Argilla
* [Semhash](https://github.com/MinishLab/semhash) by MinishLab
* [Chat Template](https://huggingface.co/docs/transformers/main/en/chat_templating) by Hugging Face

### 4. Supervised Fine-Tuning

Supervised Fine-Tuning (SFT) transforms base models into helpful assistants capable of following instructions and structuring answers effectively. Although SFT can be used to introduce new knowledge, its ability to completely learn a new language is limited. Thus, prioritizing data quality over parameter tuning is essential.

* Training Techniques: Full fine-tuning updates all parameters but requires significant computational resources. Techniques like LoRA and QLoRA update only a small number of adapter parameters while keeping the base model frozen. QLoRA further combines 4-bit quantization with LoRA to minimize VRAM usage.
* Training Parameters: Important parameters to manage include the learning rate (with schedulers), batch size, gradient accumulation, number of epochs, optimizers (e.g., 8-bit AdamW), weight decay, warmup steps, and specific LoRA parameters (rank, alpha, target modules).
* Distributed Training: Utilize multiple GPUs via frameworks such as DeepSpeed or FSDP. DeepSpeed offers ZeRO optimization stages to improve memory efficiency by partitioning state information. Both frameworks support gradient checkpointing.
* Monitoring: Keep an eye on metrics like loss curves, learning rate changes, and gradient norms, while addressing issues such as loss spikes or gradient explosions.

References:

* [Fine-tune Llama 3.1 Ultra-Efficiently with Unsloth](https://huggingface.co/blog/mlabonne/sft-llama3) by Maxime Labonne
* [Axolotl – Documentation](https://axolotl-ai-cloud.github.io/axolotl/) by Wing Lian
* [Mastering LLMs](https://parlance-labs.com/education/) by Hamel Husain
* [LoRA insights](https://lightning.ai/pages/community/lora-insights/) by Sebastian Raschka

### 5. Preference Alignment

Preference alignment is a secondary stage in the post-training process that helps fine-tune the model’s tone and reduce issues like toxicity and hallucinations. Its purpose is to improve performance and usefulness, and it generally involves methods like Direct Preference Optimization (DPO) and Proximal Policy Optimization (PPO).

* Rejection Sampling: For each prompt, generate multiple responses from the model, then score them to create on-policy data consisting of both chosen and rejected answers.
* [Direct Preference Optimization](https://arxiv.org/abs/2305.18290): This method optimizes the policy by directly increasing the likelihood of chosen responses over rejected ones, without needing a separate reward model. Although it is more computationally efficient than PPO, it may offer a slight decrease in quality.
* [Proximal Policy Optimization](https://arxiv.org/abs/1707.06347): This method iteratively updates the policy to maximize rewards while keeping changes close to the original behavior, using a reward model to score responses and requiring careful hyperparameter tuning (learning rate, batch size, and PPO clip range).
* Monitoring: Alongside SFT metrics, monitor the margin between chosen and rejected responses and track overall accuracy improvements until reaching a plateau.

References:

* [Illustrating RLHF](https://huggingface.co/blog/rlhf) by Hugging Face
* [LLM Training: RLHF and Its Alternatives](https://magazine.sebastianraschka.com/p/llm-training-rlhf-and-its-alternatives) by Sebastian Raschka
* [Preference Tuning LLMs](https://huggingface.co/blog/pref-tuning) by Hugging Face
* [Fine-tune Mistral-7b with DPO](https://mlabonne.github.io/blog/posts/Fine_tune_Mistral_7b_with_DPO.html) by Maxime Labonne
* [DPO Wandb logs](https://wandb.ai/alexander-vishnevskiy/dpo/reports/TRL-Original-DPO--Vmlldzo1NjI4MTc4) by Alexander Vishnevskiy

### 6. Evaluation

Evaluating LLMs reliably is a challenging but essential task for refining dataset composition and training settings. It is important to acknowledge Goodhart’s law: “When a measure becomes a target, it ceases to be a good measure.”

* Automated Benchmarks: Use curated datasets and metrics (such as MMLU) to assess performance on specific tasks. This approach works well for concrete tasks but may struggle with abstract capabilities and suffer from data contamination.
* Human Evaluation: Involve human assessors to prompt models and rate outputs. This method ranges from informal checks to systematic annotations and large-scale community voting (arena) and tends to work best for subjective assessments.
* Model-based Evaluation: Implement judge or reward models to assess generated responses. Although they often correlate well with human judgment, these models may be biased toward their own outputs.
* Feedback Signal: Analyze error patterns to identify shortcomings, such as problems following complex instructions, lacking specific knowledge, or being vulnerable to adversarial prompts. Use the feedback to adjust data generation and training parameters.

References:

* [Evaluation Guidebook](https://github.com/huggingface/evaluation-guidebook) by Clémentine Fourrier
* [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) by Hugging Face
* [Language Model Evaluation Harness](https://github.com/EleutherAI/lm-evaluation-harness) by EleutherAI
* [Lighteval](https://github.com/huggingface/lighteval) by Hugging Face
* [Chatbot Arena](https://lmarena.ai/) by LMSYS

### 7. Quantization

Quantization converts a model’s parameters and activations from high precision (e.g., FP32) to lower precision (such as 4 bits) to reduce compute and memory requirements.

* Base Techniques: Understand the different precisions (FP32, FP16, INT8, etc.) and basic quantization methods like absmax and zero-point techniques.
* GGUF & llama.cpp: Originally created for CPU-based runs, [llama.cpp](https://github.com/ggerganov/llama.cpp) and the GGUF format are now widely used to run LLMs on consumer hardware. They support the storage of special tokens, vocabulary, and metadata all in one file.
* GPTQ & AWQ: Methods such as [GPTQ](https://arxiv.org/abs/2210.17323) / [EXL2](https://github.com/turboderp/exllamav2) and [AWQ](https://arxiv.org/abs/2306.00978) use layer-wise calibration to maintain performance at very low bitwidths. These techniques adjust scaling dynamically and can selectively bypass or re-center the heaviest parameters.
* SmoothQuant & ZeroQuant: New methods such as SmoothQuant (which applies quantization-friendly transformations) and compiler-based optimizations like ZeroQuant help alleviate outlier issues before quantization, optimizing data flow and reducing hardware overhead.

References:

* [Introduction to Quantization](https://mlabonne.github.io/blog/posts/Introduction_to_Weight_Quantization.html) by Maxime Labonne
* [Quantize Llama models with llama.cpp](https://mlabonne.github.io/blog/posts/Quantize_Llama_2_models_using_ggml.html) by Maxime Labonne
* [4-bit LLM Quantization with GPTQ](https://mlabonne.github.io/blog/posts/4_bit_Quantization_with_GPTQ.html) by Maxime Labonne
* [Understanding Activation-Aware Weight Quantization](https://medium.com/friendliai/understanding-activation-aware-weight-quantization-awq-boosting-inference-serving-efficiency-in-10bb0faf63a8) by FriendliAI
* [SmoothQuant on Llama 2 7B](https://github.com/mit-han-lab/smoothquant/blob/main/examples/smoothquant_llama_demo.ipynb) by MIT HAN Lab
* [DeepSpeed Model Compression](https://www.deepspeed.ai/tutorials/model-compression/) by DeepSpeed

### 8. New Trends

This section covers emerging topics that do not neatly fit into other categories. Some ideas, like model merging and multimodal models, are well established, while others—such as interpretability or test-time compute scaling—are more experimental and actively researched.

* Model Merging: Merging pre-trained models has become a popular technique for boosting performance without additional fine-tuning. The [mergekit](https://github.com/cg123/mergekit) library implements several popular merging methods, including SLERP, [DARE](https://arxiv.org/abs/2311.03099), and [TIES](https://arxiv.org/abs/2311.03099).
* Multimodal Models: Models like [CLIP](https://openai.com/research/clip), [Stable Diffusion](https://stability.ai/stable-image), and [LLaVA](https://llava-vl.github.io/) are designed to process and integrate various types of inputs (text, images, audio, etc.) within a unified embedding space, enabling powerful applications such as text-to-image generation.
* Interpretability: Mechanistic interpretability approaches, including Sparse Autoencoders (SAEs) and techniques like abliteration, offer insights into the internal operations of LLMs and can allow for behavioral adjustments without retraining.
* Test-time Compute: Scaling computational resources during inference often requires multiple calls and specialized models (e.g., Process Reward Model (PRM)). Iterative procedures with fine-tuned scoring can markedly enhance performance on complex reasoning tasks.

References:

* [Merge LLMs with mergekit](https://mlabonne.github.io/blog/posts/2024-01-08_Merge_LLMs_with_mergekit.html) by Maxime Labonne
* [Smol Vision](https://github.com/merveenoyan/smol-vision) by Merve Noyan
* [Large Multimodal Models](https://huyenchip.com/2023/10/10/multimodal.html) by Chip Huyen
* [Uncensor any LLM with abliteration](https://huggingface.co/blog/mlabonne/abliteration) by Maxime Labonne
* [Intuitive Explanation of SAEs](https://adamkarvonen.github.io/machine_learning/2024/06/11/sae-intuitions.html) by Adam Karvonen
* [Scaling test-time compute](https://huggingface.co/spaces/HuggingFaceH4/blogpost-scaling-test-time-compute) by Beeching et al.

### The LLM Engineer

This part of the course teaches you how to build production-grade applications powered by LLMs, with a focus on augmenting models and deploying them.

### 1. Running LLMs

Running LLMs can be challenging given their high hardware requirements. Depending on your needs, you might opt to use an API (like GPT-4) or run a model locally. In either case, careful prompting and guidance can greatly enhance output quality and relevance.

* LLM APIs: APIs provide a convenient way to access LLMs. They are divided between private LLMs (e.g., [OpenAI](https://platform.openai.com/), [Google](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview), [Anthropic](https://docs.anthropic.com/claude/reference/getting-started-with-the-api), [Cohere](https://docs.cohere.com/docs)) and open-source LLMs (e.g., [OpenRouter](https://openrouter.ai/), [Hugging Face](https://huggingface.co/inference-api), [Together AI](https://www.together.ai/)).
* Open-source LLMs: The [Hugging Face Hub](https://huggingface.co/models) is a prime resource for finding LLMs. You can run many of these models in [Hugging Face Spaces](https://chatgpt.com/), or download and operate them locally using tools like [LM Studio](https://lmstudio.ai/), [llama.cpp](https://github.com/ggerganov/llama.cpp), or [Ollama](https://ollama.ai/).
* Prompt Engineering: Techniques such as zero-shot prompting, few-shot prompting, chain-of-thought, and ReAct are common. While these methods work better with larger models, they can be adapted for smaller ones.
* Structuring Outputs: Some tasks require outputs to follow a strict format (such as a JSON format or specific template). Tools such as [LMQL](https://lmql.ai/), [Outlines](https://github.com/outlines-dev/outlines), and [Guidance](https://github.com/guidance-ai/guidance) help ensure the generated text adheres to the required structure.

References:

* [Run an LLM locally with LM Studio](https://www.kdnuggets.com/run-an-llm-locally-with-lm-studio) by Nisha Arya
* [Prompt engineering guide](https://www.promptingguide.ai/) by DAIR.AI
* [Outlines – Quickstart](https://outlines-dev.github.io/outlines/quickstart/)
* [LMQL – Overview](https://lmql.ai/docs/language/overview.html)

### 2. Building a Vector Storage

The first step in creating a Retrieval Augmented Generation (RAG) pipeline is establishing a vector storage. This involves loading documents, splitting them into manageable pieces, and then converting key text chunks into vector embeddings for future retrieval.

* Ingesting Documents: Document loaders can process multiple formats such as PDF, JSON, HTML, and Markdown. They can also pull in data directly from databases and APIs (e.g., GitHub, Reddit, Google Drive).
* Splitting Documents: Text splitters divide documents into smaller, semantically relevant chunks. Instead of a fixed character count, splitting by headers or recursively—while preserving metadata—often yields better results.
* Embedding Models: These models transform text into vector representations, enabling a more nuanced semantic interpretation that is essential for effective search.
* Vector Databases: Databases like [Chroma](https://www.trychroma.com/), [Pinecone](https://www.pinecone.io/), [Milvus](https://milvus.io/), [FAISS](https://faiss.ai/), and [Annoy](https://github.com/spotify/annoy) are designed for storing embeddings, allowing for fast similarity-based retrieval.

References:

* [LangChain – Text splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
* [Sentence Transformers library](https://www.sbert.net/)
* [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
* [The Top 5 Vector Databases](https://www.datacamp.com/blog/the-top-5-vector-databases) by Moez Ali

### 3. Retrieval Augmented Generation

Retrieval Augmented Generation (RAG) enhances LLM outputs by using relevant contextual documents fetched from a vector database, thus improving answer accuracy without needing additional fine-tuning.

* Orchestrators: Tools like [LangChain](https://python.langchain.com/docs/get_started/introduction), [LlamaIndex](https://docs.llamaindex.ai/en/stable/), and [FastRAG](https://github.com/IntelLabs/fastRAG) connect LLMs to tools, databases, and memory systems, extending their functionality.
* Retrievers: Since user queries may not be optimized for search, techniques such as multi-query retrievers or [HyDE](https://arxiv.org/abs/2212.10496) can reformulate queries to improve retrieval performance.
* Memory: To maintain context over a conversation, LLMs use a history buffer that can be enhanced with summarization techniques or integrated with vector stores via RAG.
* Evaluation: It is crucial to assess both the document retrieval process (precision and recall) and the generation stage (faithfulness and relevancy). Tools like [Ragas](https://github.com/explodinggradients/ragas/tree/main) and [DeepEval](https://github.com/confident-ai/deepeval) can assist in these evaluations.

References:

* [Llamaindex – High-level concepts](https://docs.llamaindex.ai/en/stable/getting_started/concepts.html)
* [Pinecone – Retrieval Augmentation](https://www.pinecone.io/learn/series/langchain/langchain-retrieval-augmentation/)
* [LangChain – Q&A with RAG](https://python.langchain.com/docs/use_cases/question_answering/quickstart)
* [LangChain – Memory types](https://python.langchain.com/docs/modules/memory/types/)
* [RAG pipeline – Metrics](https://docs.ragas.io/en/stable/concepts/metrics/index.html)

### 4. Advanced RAG

In real-world scenarios, you may need to develop more complex pipelines involving SQL or graph databases, as well as systems that automatically select appropriate tools and APIs to enhance the baseline RAG setup.

* Query Construction: For structured data stored in databases, you need to translate user instructions into appropriate query languages like SQL or Cypher.
* Agents and Tools: LLM agents can automatically choose the most suitable tools—ranging from simple web searches (e.g., Google, Wikipedia) to complex systems (e.g., Python interpreters, Jira)—to answer queries.
* Post-Processing: Enhance the overall relevance of retrieved documents using re-ranking methods, [RAG-fusion](https://github.com/Raudaschl/rag-fusion), or classification techniques.
* Program LLMs: Frameworks like [DSPy](https://github.com/stanfordnlp/dspy) allow you to fine-tune prompts and model parameters programmatically based on automated evaluations.

References:

* [LangChain – Query Construction](https://blog.langchain.dev/query-construction/)
* [LangChain – SQL](https://python.langchain.com/docs/use_cases/qa_structured/sql)
* [Pinecone – LLM agents](https://www.pinecone.io/learn/series/langchain/langchain-agents/)
* [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) by Lilian Weng
* [LangChain – OpenAI’s RAG](https://blog.langchain.dev/applying-openai-rag/)
* [DSPy in 8 Steps](https://dspy-docs.vercel.app/docs/building-blocks/solving_your_task)

### 5. Inference Optimization

Since generating text is computationally intensive, several techniques exist to maximize throughput and reduce inference costs alongside quantization.

* Flash Attention: Optimizes the attention mechanism by reducing its complexity from quadratic to linear, thereby speeding up both training and inference.
* Key-value Cache: Learn about the key-value cache and enhancements like [Multi-Query Attention](https://arxiv.org/abs/1911.02150) (MQA) and [Grouped-Query Attention](https://arxiv.org/abs/2305.13245) (GQA).
* Speculative Decoding: Use a smaller model to produce draft outputs that are later refined by a larger model, thus accelerating text generation.

References:

* [GPU Inference](https://huggingface.co/docs/transformers/main/en/perf_infer_gpu_one) by Hugging Face
* [LLM Inference](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices) by Databricks
* [Optimizing LLMs for Speed and Memory](https://huggingface.co/docs/transformers/main/en/llm_tutorial_optimization) by Hugging Face
* [Assisted Generation](https://huggingface.co/blog/assisted-generation) by Hugging Face

### 6. Deploying LLMs

Deploying LLMs, especially at scale, is complex and may require multiple GPU clusters. However, demos or local applications often have simpler requirements.

* Local Deployment: Open-source LLMs offer privacy advantages over private models. Solutions such as [LM Studio](https://lmstudio.ai/), [Ollama](https://ollama.ai/), [oobabooga](https://github.com/oobabooga/text-generation-webui), and [kobold.cpp](https://github.com/LostRuins/koboldcpp) facilitate local deployment.
* Demo Deployment: Tools like [Gradio](https://www.gradio.app/) and [Streamlit](https://docs.streamlit.io/) are excellent for prototyping apps and sharing demos. They are also easy to host online (for example, on [Hugging Face Spaces](https://huggingface.co/spaces)).
* Server Deployment: Running LLMs at scale often demands cloud infrastructure (or on-prem solutions) and specialized frameworks such as [TGI](https://github.com/huggingface/text-generation-inference) or [vLLM](https://github.com/vllm-project/vllm/tree/main).
* Edge Deployment: In resource-constrained environments, frameworks like [MLC LLM](https://github.com/mlc-ai/mlc-llm) and [mnn-llm](https://github.com/wangzhaode/mnn-llm/blob/master/README_en.md) enable deployment on web browsers, Android, and iOS.

References:

* [Streamlit – Build a basic LLM app](https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps) by Streamlit
* [HF LLM Inference Container](https://huggingface.co/blog/sagemaker-huggingface-llm) by Hugging Face
* [Philschmid blog](https://www.philschmid.de/) by Philipp Schmid
* [Optimizing Latency](https://hamel.dev/notes/llm/inference/03_inference.html) by Hamel Husain

### 7. Securing LLMs

LLM applications bring their own unique security challenges in addition to standard software vulnerabilities.

* Prompt Hacking: This includes issues like prompt injection (where unwanted instructions hijack the model), data/prompt leaking (extracting the original prompt or training data), and jailbreaking (bypassing the model’s safety features).
* Backdoors: These attacks can target training data by poisoning it with false or malicious content, or by introducing hidden triggers that alter model behavior during inference.
* Defensive Measures: Protect your LLM applications by testing them for vulnerabilities using techniques such as red teaming and tools like [garak](https://github.com/leondz/garak/), while monitoring in production with frameworks like [langfuse](https://github.com/langfuse/langfuse).

References:

* [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) by HEGO Wiki
* [Prompt Injection Primer](https://github.com/jthack/PIPE) by Joseph Thacker
* [LLM Security](https://llmsecurity.net/) by [@llm_sec](https://twitter.com/llm_sec)
* [Red teaming LLMs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/red-teaming) by Microsoft