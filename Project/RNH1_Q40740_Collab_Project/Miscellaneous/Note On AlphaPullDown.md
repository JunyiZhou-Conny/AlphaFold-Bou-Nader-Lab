Great. I’ll look into:

1. Whether the AlphaPulldown-provided feature database is a suitable and effective substitute for running `create_individual_features.py` locally.
2. How to integrate and use this feature database in your local AlphaPulldown pipeline (file format, directory structure, and usage instructions).
3. Whether it’s feasible and practical to install and run ColabFold locally with GPU-accelerated MMseqs2 on your cluster with 7 NVIDIA A5000 GPUs. I’ll find clear installation steps and any existing guides or experiences from others.

I’ll update you shortly with everything you need.

# 1. Using the AlphaPulldown Precomputed Features Database vs. Local Generation

**AlphaPulldown’s features database** provides precomputed input features (MSAs, templates, etc.) for proteins from many model organisms, and it can effectively replace running the local feature generation script in those cases ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=To%20enable%20faster%20usage%20and,html)). In fact, the database contains **all the same data** that `create_individual_features.py` would produce for a given sequence – including multiple sequence alignments (MSAs) and template search results – packaged as Alphafold feature pickles. The database covers entire proteomes for major organisms (e.g. *Homo sapiens*, *E. coli*, *Yeast*, *Drosophila*, *Mouse*, *Arabidopsis*, etc.) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=To%20enable%20faster%20usage%20and,html)) ([AlphaPulldown - Root Index](https://alphapulldown.s3.embl.de/index.html#:~:text=,Homo_sapiens)), so if your protein of interest is among these, you can download its feature file instead of recomputing. AlphaPulldown’s documentation explicitly notes that if you work with proteins from these model organisms, you can **skip the features computation step** by using the precomputed files ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=1,CPU%20stage)). 

One caveat: the current database’s MSA features are missing certain pairing information used by Alphafold-Multimer (i.e. linking sequences from the same species in complex MSAs), which **could slightly reduce multimer accuracy** ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=Warning)). (The developers are aware and working to fix this.) Aside from that, the feature files are essentially complete and ready to use. Each file (a Python pickle, `.pkl`) contains the sequence’s aligned homologs, evolutionary profiles, and any template structures found up to the specified date – just as if you had run Alphafold’s data pipeline on that sequence. In summary, for proteins available in the AlphaPulldown features database, you can trust these files to **replace local feature generation** and feed directly into the structure prediction step, saving considerable time on MSAs and template searches.

# 2. Downloading and Integrating the Precomputed Feature Database

To use the AlphaPulldown features database locally, you’ll need to **download the relevant feature files** and set up AlphaPulldown to recognize them. The files are hosted on an S3 bucket (at `alphapulldown.s3.embl.de`), organized by organism. Each protein’s feature is stored as a compressed pickle (`.pkl.xz`) named by its UniProt ID ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=List%20available%20organisms%3A)). For example, the human protein with UniProt ID Q6BF25 would be in `Homo_sapiens/Q6BF25.pkl.xz` ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=List%20available%20organisms%3A)) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=For%20example%2C%20to%20download%20the,Q6BF25%20from%20Escherichia%20coli%2C%20use)). The recommended way to fetch data is using the MinIO client (`mc`), which lets you treat the S3 storage like a filesystem:

**Steps to download and set up the features database:**

1. **Install the MinIO CLI** (`mc`): Download the binary from MinIO (for Linux: `https://dl.min.io/client/mc/release/linux-amd64/mc`), make it executable, and put it in your `$PATH` ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=Example%20for%20AMD64%20architecture%3A)).  
2. **Configure S3 access**: Set up an alias for the EMBL S3 bucket. For example:  
   ```bash
   mc alias set embl https://s3.embl.de "" "" --api S3v4
   ```
   This lets you refer to the repository as `embl/alphapulldown`.  
3. **List available organisms**: Run `mc ls embl/alphapulldown/input_features` to see directories for each organism (e.g. `Homo_sapiens/`, `Escherichia_coli/`, etc.) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=List%20available%20organisms%3A)).  
4. **Download specific protein features**: If you need a particular protein, copy its file by UniProt ID. For example:  
   
   ```bash
   mc cp embl/alphapulldown/input_features/Escherichia_coli/Q6BF25.pkl.xz  ./Q6BF25.pkl.xz
   ```
   This command downloads the compressed feature file for **UniProt Q6BF25** (from *E. coli*) to the current directory ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=For%20example%2C%20to%20download%20the,Q6BF25%20from%20Escherichia%20coli%2C%20use)). After downloading, you can optionally decompress it (`unxz Q6BF25.pkl.xz`) to get `Q6BF25.pkl`.  
5. **Download an entire proteome (optional)**: To retrieve all features for an organism, use a recursive copy or mirror. For example:  
   ```bash
   mc cp --recursive embl/alphapulldown/input_features/Homo_sapiens/ ./Homo_sapiens/
   ```
   This will download every `.pkl.xz` in the human directory into a local folder `Homo_sapiens/` ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=Download%20all%20features%20for%20an,organism)). (You can similarly mirror directories to keep them in sync.)  
6. **Organize the files**: Ensure the downloaded files are stored in a directory structure that matches your usage. If you copied whole organism folders, you might have `.../input_features/Organism/ID.pkl.xz`. You can also consolidate all `.pkl.xz` files in one folder if preferred. The key is that you know the path to these feature files and their filenames correspond to the protein identifiers you will use. *Tip:* If your input FASTA uses UniProt IDs as sequence names, AlphaPulldown will directly match those to the filenames. Otherwise, you may need to rename the files or FASTA headers accordingly so they correspond (e.g. “>Q6BF25” in FASTA to use `Q6BF25.pkl.xz`).  
7. **Configure AlphaPulldown to use these features**: Open your AlphaPulldown `config.yaml` (or ensure you’ll pass the right flags) to point to the feature files. In the config, set:  
   ```yaml
   feature_directory:
     - "/path/to/directory/with/features/"
   ```
   This path should be the folder containing the `.pkl` or `.pkl.xz` files ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=feature_directory%20%3A%20)). If you kept the organism subfolders, you can list those parent directories here as well. **Important:** if the files are still compressed (with `.xz`), enable the compression flag so AlphaPulldown knows to load them. You can do this by setting `--compress-features=True` on the command-line or in the config (AlphaPulldown’s docs note that otherwise it won’t recognize the files) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=Note)). Alternatively, you can pre-decompress the files to plain `.pkl` (which uses more disk space but avoids needing the flag).  
8. **Verify usage**: When you run AlphaPulldown’s pipeline, it should detect the presence of feature files and skip creating new ones. For example, running the structure prediction step (`run_multimer_jobs.py` or the Snakemake pipeline) will load the existing pickles from `feature_directory` instead of invoking `create_individual_features.py`. If using the two-step manual pipeline, you can simply **omit the first step** entirely – or run it with `--skip_existing=True` so it doesn’t overwrite or redo features that already exist.

After integration, AlphaPulldown will use the downloaded feature data transparently. Your directory with feature files essentially serves as a **local cache of precomputed MSAs and templates**, dramatically speeding up the pipeline. Just keep in mind that this database is limited to the organisms provided – for any protein not in the database, you’d still need to run the feature creation step or use an alternative method (see next section for using ColabFold to generate features).

# 3. Installing ColabFold Locally with GPU-Accelerated MMseqs2

Installing and running **ColabFold** on a local HPC cluster (especially one with multiple GPUs) is a practical way to accelerate AlphaFold/AlphaPulldown feature generation and prediction. ColabFold is a community-supported wrapper of AlphaFold2 that replaces the slow Jackhmmer/HHblits searches with much faster **MMseqs2** searches (and can leverage GPUs for even greater speed) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=MMseqs2%20is%20another%20method%20for,installation%20of%20databases%20is%20needed)). Many users have successfully deployed ColabFold on local machines and clusters (the **LocalColabFold** project provides scripts and there is an active community), so you won’t be on your own – it’s a well-trodden path. The main considerations are **installation complexity** (managing dependencies like CUDA/Jax, and downloading large databases) and ensuring your cluster environment is set up to use GPUs for the search.

 ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/)) *Figure: Local ColabFold with GPU-accelerated MMseqs2 dramatically reduces MSA+structure prediction time per protein (green bar) compared to the standard AlphaFold2 pipeline (gray bar). In a benchmark on CASP14 targets, ColabFold’s GPU pipeline took ~105 seconds vs. ~2277 seconds for Alphafold2 – roughly a **22× speedup** with no loss in accuracy ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/#:~:text=Speed%20improvement)). This uses one NVIDIA GPU; using multiple GPUs can further boost throughput ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/#:~:text=High%20throughput%20and%20scalability)).*  

In terms of **benefits**, a local ColabFold setup can cut down MSA computation from minutes to seconds per sequence by using MMseqs2’s fast search algorithm (especially with the new GPU-accelerated version). In one comparison, ColabFold with MMseqs2-GPU was ~22× faster than Alphafold’s default pipeline (which relies on CPU tools like Jackhmmer/HHblits) for single-protein predictions ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/#:~:text=Speed%20improvement)). Importantly, this speedup doesn’t compromise accuracy – you get the same quality inputs and outputs, just generated much more quickly. Moreover, ColabFold supports multi-sequence and protein-complex inputs, and it can utilize **multiple GPUs in parallel** (or even in tandem for huge databases), allowing you to scale up throughput on a 7×GPU cluster ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/#:~:text=High%20throughput%20and%20scalability)). The trade-off is the initial setup effort: you’ll need to install the ColabFold software environment and obtain the large sequence databases for local use (hundreds of GBs), and ensure your MMseqs2 installation is compiled with GPU support. Overall, if you have the technical resources, running ColabFold locally is **both feasible and advantageous** for high-performance structure prediction pipelines.

## Installation and Setup for Local ColabFold

To run ColabFold on your cluster, you should set up a Python environment with the ColabFold package, AlphaFold’s code, and the proper GPU-enabled dependencies (like JAX and CUDA tools), and install MMseqs2 for sequence searching. Here’s a step-by-step guide:

1. **Prepare a Python environment**: On your cluster login node, create a new environment (conda or virtualenv) with a compatible Python version (Python 3.8–3.10 is recommended). Activate the environment. Make sure the NVIDIA CUDA drivers and libraries on the cluster are up to date (ColabFold’s latest versions require CUDA 12+ and cudnn 8+ on the system – check with your admins if needed).  
2. **Install ColabFold and AlphaFold code**: ColabFold can be installed via pip. The latest method is to install from the GitHub source with the “alphafold” extra, which pulls in AlphaFold’s open-source code. For example:  
   ```bash
   pip install "colabfold[alphafold] @ git+https://github.com/sokrypton/ColabFold"
   ```
   This will fetch ColabFold and the necessary AlphaFold scripts/models into your environment ([ColabFold Downloads](https://colabfold.mmseqs.com/#:~:text=pip%20install%20,releases%2Fjax_cuda_releases.html%20colabfold_search%20input_sequences.fasta%20database%2F%20msas)). (Alternatively, you could use the **LocalColabFold** installer script or a Docker container, but using pip gives you control within your HPC environment.)  
3. **Install JAX with CUDA support**: AlphaFold relies on Google’s JAX library for GPU computations. You must install a JAX version matching your CUDA toolkit. ColabFold documentation suggests, for CUDA 11/12, a command like:  
   ```bash
   pip install -q "jax[cuda]>=0.3.8,<0.4" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
   ```
   This will download the correct pre-built JAX CUDA wheel (ensure it corresponds to your CUDA version) ([ColabFold Downloads](https://colabfold.mmseqs.com/#:~:text=pip%20install%20,releases%2Fjax_cuda_releases.html%20colabfold_search%20input_sequences.fasta%20database%2F%20msas)). Make sure this step installs **jaxlib** with CUDA – you can verify by launching Python and importing jax to see if it recognizes the GPU.  
4. **(Optional) Install OpenMM for relaxation**: If you plan to use AlphaFold’s Amber relaxation on predicted structures, you should install OpenMM (e.g., via conda). ColabFold can skip relaxation by default, so this is optional unless needed.  
5. **Install MMseqs2 (GPU version)**: ColabFold’s speed comes from MMseqs2, which you need to have locally. The **easiest way** is to download a precompiled MMseqs2 binary with GPU support. The MMseqs2 developers provide such binaries – for example:  
   ```bash
   wget https://mmseqs.com/latest/mmseqs-linux-gpu.tar.gz
   tar -xzf mmseqs-linux-gpu.tar.gz
   export PATH="$PWD/mmseqs/bin:$PATH"
   ```
   This downloads the latest MMseqs2 (with GPU code) and adds it to your PATH. The GPU build requires an NVIDIA GPU of Ampere generation or newer (A5000 is Ampere, so that’s fine) and will fall back to CPU if no GPU is available ([Index of /latest/](https://mmseqs.com/latest/#:~:text=...%20gpu,Mar)) ([[PDF] MMseqs2 User Guide](https://mmseqs.com/latest/userguide.pdf#:~:text=wget%20https%3A%2F%2Fmmseqs.com%2Flatest%2Fmmseqs,newer%20for%20full%20speed%2C)). *Alternatively, you can compile MMseqs2 from source with GPU flags, but the provided binaries save time.*  
6. **Download sequence databases for ColabFold**: This is the most time- and storage-consuming step. ColabFold uses a reduced set of sequence databases: UniRef30, and either BFD+MGnify or the “ColabFold DB” (which is BFD/MGnify plus a lot of environmental sequences). The total size is roughly **940 GB** for the full set ([GitHub - sokrypton/ColabFold: Making Protein folding accessible to all!](https://github.com/sokrypton/ColabFold#:~:text=Generating%20MSAs%20for%20large%20scale,structure%2Fcomplex%20predictions)). ColabFold provides a script to automate the download and formatting:  
   ```bash
   wget https://raw.githubusercontent.com/sokrypton/ColabFold/main/setup_databases.sh  
   chmod +x setup_databases.sh  
   ./setup_databases.sh /path/to/db_folder
   ```
   Point this to a filesystem with enough space (close to 1 TB). This will fetch and prepare UniRef30 and BFD/MGnify by default, converting them into MMseqs2’s searchable format ([GitHub - sokrypton/ColabFold: Making Protein folding accessible to all!](https://github.com/sokrypton/ColabFold#:~:text=First%20create%20a%20directory%20for,take%20a%20couple%20of%20hours)). (By default, it might skip the larger ColabFold-DB unless specified, to save space.) If you prefer using the comprehensive ColabFold DB instead of BFD, check the script options – but note it will need more memory to search. After this, you should have a `db_folder` containing folders like `uniref30_2303_db` and `bfd.mgnify30.metaeuk30.smag30` with `.db` files and indices.  
7. **Verify the setup**: At this point, you have ColabFold installed and databases ready. Ensure you have the AlphaFold model parameter files as well – if not, ColabFold might prompt to download them on first run (~3GB for all Alphafold2 models). You can download them in advance by running `colabfold_batch` once, or by using the script provided in the AlphaPulldown/AlphaFold setup (AlphaPulldown’s install guide references downloading AlphaFold params if not done ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=can%20alternatively%20use%20the%20remotely,downloading%20and%20executing%20this%20script))). Now you’re ready to generate MSAs or predictions.

## Generating MSAs and Integrating ColabFold into the Pipeline

Once installation is complete, you can use ColabFold in two modes: (a) **generate MSAs (and possibly templates) as input features** for use in AlphaPulldown/AlphaFold, or (b) **perform full structure predictions** with ColabFold’s own pipeline. Here we focus on using ColabFold to replace the feature generation (`create_individual_features.py` stage) in AlphaPulldown, since that was the goal.

**Using ColabFold to create MSAs (batch mode):**

1. **Run the colabfold_search for your sequences**: ColabFold provides a CLI called `colabfold_search` which uses your local MMseqs2 and databases to find homologous sequences. Prepare a FASTA file with all your query protein sequences (for multiple sequences, ColabFold allows concatenating them separated by null characters `\0`, but an easier method is usually to run a search for all sequences at once in a multi-FASTA). For example, if you have `queries.fasta`, run:  
   ```bash
   colabfold_search queries.fasta /path/to/db_folder msas_out
   ```
   This will search the UniRef30 and BFD/MGnify databases and output the alignments in an `msas_out/` directory ([GitHub - sokrypton/ColabFold: Making Protein folding accessible to all!](https://github.com/sokrypton/ColabFold#:~:text=,a%20GPU%20colabfold_batch%20msas%20predictions)). By default, each query sequence results in two alignment files: a `uniref.a3m` (from UniRef30) and a `bfd.mgnify30.metaeuk30.smag30.a3m` (from the environmental sequence database) ([ColabFold Downloads](https://colabfold.mmseqs.com/#:~:text=colabfold_search%20input_sequences)). The search step is CPU-intensive (and can also use GPU for the initial filtering). On a cluster, you might want to run this on a compute node with a lot of CPUs (and optionally a GPU); MMseqs2 can utilize multiple threads and multiple GPUs if available ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/#:~:text=High%20throughput%20and%20scalability)). *Tip:* For large numbers of queries, MMseqs2 can do a batch search efficiently, but ensure you have enough RAM (128 GB+ is recommended for the full database index) or remove the precomputed index to let it build on-the-fly if memory is limited ([ColabFold Downloads](https://colabfold.mmseqs.com/#:~:text=Searches%20against%20the%20ColabFoldDB%20can,the%20index%20is%20in%20memory)).  
2. **Rename MSA files to match protein IDs**: If you searched multiple sequences at once, the output `.a3m` files may be named generically (like `0.a3m`, `1.a3m`, etc., or by sequence hash). AlphaPulldown provides a helper script `rename_colab_search_a3m.py` to rename these to the original FASTA identifiers ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=These%20a3m%20files%20from%20,py%20and%20run)). Run this script on the output directory, providing the original FASTA path:  
   ```bash
   python rename_colab_search_a3m.py msas_out queries.fasta
   ```
   After this, your `msas_out` folder will contain files like `proteinA.a3m`, `proteinB.a3m`, etc., corresponding to the `>proteinA`, `>proteinB` headers in your FASTA ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=output_dir%20%7C,)). Verify that each query sequence’s name now matches an `.a3m` file. (This step is important so that AlphaPulldown knows which alignment belongs to which sequence.)  
3. **Generate the feature pickles using the MSAs**: Now that you have the MSAs, you can run the AlphaPulldown feature script in a mode that consumes those alignments instead of recomputing them. Use the same FASTA as input, specify the output directory as the one with your `.a3m` files, and add the flags `--use_mmseqs2=True` and `--skip_existing=False`. For example:  
   ```bash
   source activate AlphaPulldown  # activate AP conda env  
   create_individual_features.py \
     --fasta_paths=queries.fasta \
     --data_dir=<path to Alphafold DBs> \
     --output_dir=msas_out \
     --use_mmseqs2=True \
     --skip_existing=False 
   ```
   AlphaPulldown will detect the pre-existing `*.a3m` files for each sequence and load them (instead of calling HMMER or the remote server) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=create_individual_features.py%20%5C%20,run%20all%20one%20after%20another)). It will then perform any remaining steps like pairing up MSAs for complexes (if applicable) and searching for templates using the normal Alphafold database (PDB70 or PDB, as configured). Finally, it writes out the `.pkl` feature files for each protein in `msas_out` (alongside the `.a3m`). After this runs, you should see `proteinA.pkl`, `proteinB.pkl`, etc., next to your alignment files ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=output_dir%20%7C,proteinC.pkl)). These pickles are now ready to be used for AlphaPulldown’s prediction step (or any Alphafold run) just as if you had generated them with the default pipeline.  
4. **Proceed with AlphaPulldown predictions**: With the feature files in place, you can run the second step of AlphaPulldown (e.g. `run_multimer_jobs.py` with your desired mode) pointing to `--monomer_objects_dir=msas_out` (or by ensuring config `feature_directory` includes `msas_out`). AlphaPulldown will load the `.pkl` features for each protein and carry out complex predictions as usual. You have effectively **replaced the slow CPU MSA generation with ColabFold’s fast search**.

If instead you want to use ColabFold directly for structure prediction (bypassing AlphaPulldown for some cases), you can do so with the `colabfold_batch` command. For example:  
```bash
colabfold_batch queries.fasta predictions_out/ --num-recycle 3 --use-gpu-relax
```
This would perform the whole pipeline (MSA search and structure prediction) for the sequences (including multimer modeling if you provide a complex in the input). ColabFold can accept a CSV or FASTA specifying protein complexes as well. However, note that AlphaPulldown offers specialized workflows (like flexible combinations, custom templates, cross-link integration) that plain ColabFold doesn’t have, so integrating ColabFold’s MSA generation into AlphaPulldown (as described above) is often the best of both worlds for high-throughput complex predictions.

**Practical considerations & support:** Setting up ColabFold locally does involve a number of dependencies, but there is community support (forums, GitHub issues) and even installer scripts (like LocalColabFold) to simplify it. Make sure your cluster’s GPUs are CUDA-compatible with the versions of JAX and drivers needed (for example, newer ColabFold requires CUDA 12+; if your drivers are older, you might need an older ColabFold/Jax version or to update drivers). Running on HPC with 7 GPUs means you can parallelize jobs – e.g., run multiple `colabfold_search` or `colabfold_batch` processes at once, or let MMseqs2 itself use multiple GPUs for one large search job ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/#:~:text=High%20throughput%20and%20scalability)). MMseqs2 GPU support is relatively new, so if you encounter issues (e.g., with certain database index steps), check the MMseqs2 GitHub for known bugs or consider using the CPU search as a fallback for those parts. Overall, **installing ColabFold locally is quite feasible** and, once set up, it provides substantial performance gains. The combination of AlphaPulldown + ColabFold (local) can greatly speed up your protein-protein screening pipeline while keeping everything in-house (no data sent to external servers) – a clear win for high-performance computing environments.

**Sources:** The AlphaPulldown README and GitHub issues were consulted for details on the features database and integration options ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=Instead%20of%20generating%20feature%20files,features%20for%20major%20model%20organisms)) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=feature_directory%20%3A%20)) ([GitHub - KosinskiLab/AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown#:~:text=create_individual_features.py%20%5C%20,run%20all%20one%20after%20another)). ColabFold’s documentation and NVIDIA’s technical blog provide information on local installation and performance of MMseqs2-GPU ([ColabFold Downloads](https://colabfold.mmseqs.com/#:~:text=pip%20install%20,releases%2Fjax_cuda_releases.html%20colabfold_search%20input_sequences.fasta%20database%2F%20msas)) ([Boost Alphafold2 Protein Structure Prediction with GPU-Accelerated MMseqs2 | NVIDIA Technical Blog](https://developer.nvidia.com/blog/boost-alphafold2-protein-structure-prediction-with-gpu-accelerated-mmseqs2/#:~:text=Speed%20improvement)). These resources guided the step-by-step instructions and considerations above.







Research Log for Charles

Protein sequences:

[https://www.uniprot.org](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Fwww.uniprot.org%2F&data=05|02|junyi.zhou@emory.edu|480d33464c5946848f4508dd586d837b|e004fb9cb0a4424fbcd0322606d5df38|0|0|638763950141257455|Unknown|TWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D|0|||&sdata=6zcXIWqwYe6Es1nwN10ybmI4ZQkQ83rCVlG%2FwB8clYs%3D&reserved=0)



AlphaPullDown:

[https://academic.oup.com/bioinformatics/article/39/1/btac749/6839971](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Facademic.oup.com%2Fbioinformatics%2Farticle%2F39%2F1%2Fbtac749%2F6839971&data=05|02|junyi.zhou@emory.edu|480d33464c5946848f4508dd586d837b|e004fb9cb0a4424fbcd0322606d5df38|0|0|638763950141281560|Unknown|TWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D|0|||&sdata=rqxW17D33IGCxpGbtu77s4VgA%2FeFJg6KREs1gVhY5sw%3D&reserved=0)



[https://github.com/KosinskiLab/AlphaPulldown](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2FKosinskiLab%2FAlphaPulldown&data=05|02|junyi.zhou@emory.edu|480d33464c5946848f4508dd586d837b|e004fb9cb0a4424fbcd0322606d5df38|0|0|638763950141295645|Unknown|TWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D|0|||&sdata=uG%2FUwqyEXFZUQrunrOjfPOK8NhHqXtDmpMduwap39DI%3D&reserved=0)



AF2-multimer

[https://sbgrid.org//wiki/examples/alphafold2](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Fsbgrid.org%2Fwiki%2Fexamples%2Falphafold2&data=05|02|junyi.zhou@emory.edu|480d33464c5946848f4508dd586d837b|e004fb9cb0a4424fbcd0322606d5df38|0|0|638763950141313481|Unknown|TWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D|0|||&sdata=nOYFb4BN%2FJecjAz2ahncs4dBr7G4gxLWbnwQuJpQkwE%3D&reserved=0)



[https://github.com/google-deepmind/alphafold#readme](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2Fgoogle-deepmind%2Falphafold%23readme&data=05|02|junyi.zhou@emory.edu|480d33464c5946848f4508dd586d837b|e004fb9cb0a4424fbcd0322606d5df38|0|0|638763950141326069|Unknown|TWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D|0|||&sdata=6UPxZGUUaB8Uobit%2FOpmAiBqdTLuidsh%2FYYYabY%2FcNI%3D&reserved=0)



AF3

[https://alphafoldserver.com/welcome](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Falphafoldserver.com%2Fwelcome&data=05|02|junyi.zhou@emory.edu|480d33464c5946848f4508dd586d837b|e004fb9cb0a4424fbcd0322606d5df38|0|0|638763950141337367|Unknown|TWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D|0|||&sdata=23nvi%2B4Z3UaBXHEhgpVyH48wkUtzU6TO6UcJG7cdHKY%3D&reserved=0)



[https://github.com/google-deepmind/alphafold3](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2Fgoogle-deepmind%2Falphafold3&data=05|02|junyi.zhou@emory.edu|480d33464c5946848f4508dd586d837b|e004fb9cb0a4424fbcd0322606d5df38|0|0|638763950141351125|Unknown|TWFpbGZsb3d8eyJFbXB0eU1hcGkiOnRydWUsIlYiOiIwLjAuMDAwMCIsIlAiOiJXaW4zMiIsIkFOIjoiTWFpbCIsIldUIjoyfQ%3D%3D|0|||&sdata=xZny7G41yE%2BGp46GIPntJksfVA4F4ttFMbtcIZwBWPo%3D&reserved=0)

Several types of data I would expect from AF3:

1. mmCIF, the predicted 3D structure of the protein complex
2. pLDDT: predicted local distance difference, per-residue score indciates the confidence of the model in the positioning of individual residues, higher value means greater reliability





There is a section on UniProt that informs us how to access the website with programs. All resources are accessible using URLs (REST)



REST (Representatinal State Transfer) is an architectural style for designing web services. It allows programs to interact with web sources using HTTP requests



There are several HTTP methods to perform operations on resources, typically represented as URLs: GET, POST, PUT, DELETE

https://www.uniprot.org/uniprotkb/Q04740/entry



go to my home directory

conda is available for all users

1. create ocnda environment

conda create -n AlphaPulldown -c omnia -c bioconda -c conda-forge python==3.11 openmm==8.0 pdbfixer==1.9 kalign2 hhsuite hmmer modelcif

source activate AlphaPulldown



2. create environment

pip install -U "jax[cuda12]"



3. the github recommends installing the downstream analysis tools, but I will hold off at the moment 



4. script execution

source activate AlphaPulldown

create_individual_features.py \

 --fasta_paths=<sequences.fasta> \

 --data_dir=<path to alphafold databases> \

 --output_dir=<dir to save the output objects> \ 

 --max_template_date=<any date you want, format like: 2050-01-01> \



export FASTA_PATHS="/data7/Conny/data/single_sequence.fasta”

export DATA_DIR="/data7/Conny/data/DOWNLOAD_DIR"

export OUTPUT_DIR="/data7/Conny/result_JackHMMer”

export MAX_TEMPLATE_DATE="2025-03-24”



5. before executing the code, move files from local computer to cloud. SSH, scp, stored in the root directory where we see data7

mv sequences.fasta protein_list1.txt protein_list2.txt /data7/alphapulldown_project/

scp /Users/conny/Desktop/AlphaFold/protein_sequences_continue.fasta username@cluster_ip:/remote/path/ jzho349@kilimanjaro.biochem.emory.edu:/data7/Conny/data







6. This step is not necesssary, i need to download the alphafold database, a genetic database for feature extraction not downloading the feature directly. but perhaps the prioris worth trying as perhaps some protein is pretty common and people once performed feature extraction on them, anyway 

install **MinIO Client (mc)** to access the **Features Database** required by your AlphaPulldown script.

server is running **Linux (Workstation 8.11.3) on AMD EPYC**



Download mc binary for AMD64

curl -O https://dl.min.io/client/mc/release/linux-amd64/mc

Make It Executable

chmod +x mc

Move It to a Personal Bin Directory

mkdir -p $HOME/bin

mv mc $HOME/bin/

Add It to Your PATH

export PATH=$HOME/bin:$PATH

To make this permanent, add it to your ~/.bashrc or ~/.bash_profile:

echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc

source ~/.bashrc



real 6. go to alphafold website

[https://sbgrid.org/wiki/examples/alphapulldown_example#:~:text=These%20databases%20can%20be%20downloaded,amount%20of%20time%20to%20download.](https://sbgrid.org/wiki/examples/alphapulldown_example#:~:text=These databases can be downloaded,amount of time to download.)

https://github.com/deepmind/alphafold#genetic-databases



/programs/x86_64-linux/alphafold/2.3.2/alphafold/scripts/download_all_data.sh /data7/Conny/alphafold_genetic_db



7. aria2 installed

still the download all script is missing, go to alphafold github and download the full scripts

https://github.com/KosinskiLab/alphafold/tree/main/scripts

the download takes about 19 hours, so pretty long, and as i am performing the next stage, it appears that one of the database is incomptaible with the requirement of alphapulldown, specifically this command here

bash "${SCRIPT_DIR}/download_uniref30.sh" "${DOWNLOAD_DIR}”



8. I update the uniref30 database, this seems to be an reoccuring issue, and I saw a solution to it online on github: https://github.com/google-deepmind/alphafold/pull/860/files



9. In the process of running create_individual_feature.py

\- using alphafold/HHBlits methods

\- Working only with 1 protein right now



![Pasted Graphic.png](blob:file:///c00c6532-5576-478f-a9ae-9848ca92155b)





10. Running alphafold database is taking so long, decide to try out the mmseqs2. there are 2 options, remotely running or locally, first try remote running

source activate AlphaPulldown

create_individual_features.py \

 --fasta_paths=/data7/Conny/data/protein_sequences_continue.fasta \

 --data_dir=/data7/Conny/data/DOWNLOAD_DIR \

 --output_dir=/data7/Conny/result_mmseqs2 \

 --use_mmseqs2=True \

 --skip_existing=False \

 --max_template_date=2025-03-23





Run using MMseqs2 and ColabFold databases (faster):



MMSeqs2 and ColabFold allow for much quicker calculation of MSAs than the default AlphaFold method above. To use MMSeqs2 in AlphaPulldown, please refer to [this manual](https://github.com/KosinskiLab/AlphaPulldown/blob/main/manuals/mmseqs2_manual.md).

📝 Please be aware that MMseqs2/ColabFold and AlphaFold/HHBlits methods give different MSAs. Therefore, the resulting models may be also different. However, the models from these two pipelines usually have a comparable accuracy.

While running th script, one specific protein faces an issue P40449, P23369, Q12754

\- To nano into a file and delete a specific line do control+shift+6, and then arrow to the place you want to delete





\# === User-configurable paths ===

export FASTA_PATH="/data7/Conny/data/protein_sequences.fasta"

export DATA_DIR="/data7/Conny/data/AF_GeneticDB"

export OUTPUT_DIR="/data7/Conny/result_mmseqs2"

export MAX_TEMPLATE_DATE="2025-03-25"



create_individual_features.py \

 --fasta_paths="$FASTA_PATH" \

 --data_dir="$DATA_DIR" \

 --output_dir="$OUTPUT_DIR" \

 --use_mmseqs2=True \

 --skip_existing=True \

 --max_template_date="$MAX_TEMPLATE_DATE"



export FASTA_PATH="/data7/Conny/data/protein_sequences.fasta"

export DATA_DIR="/data7/Conny/data/AF_GeneticDB"

export OUTPUT_DIR="/data7/Conny/result_JackHMMer"

export MAX_TEMPLATE_DATE="2025-03-25"



create_individual_features.py \

 --fasta_paths="$FASTA_PATH" \

 --data_dir="$DATA_DIR" \

 --output_dir="$OUTPUT_DIR" \

 --use_mmseqs2=False \

 --skip_existing=True \

 --max_template_date="$MAX_TEMPLATE_DATE"





11. Ways to get around the 1.5 months running

\- Using more CPU threads, failed for now, increasing the CPU threads does not seem to affect the running of JackHMMer

\- Download it from feature database: the database contains all the same data that create_individual_features.py would produce for a given sequence – including multiple sequence alignments (MSAs) and template search results – packaged as Alphafold feature pickles

Warning: The MSA features in this database do not include information necessary for pairing sequences from the same species, which may result in reduced accuracy. We are working on fixing this.





Mar 24th After Talking to Charles

\- Keep running mmseqs2 and keep tracking of protein that goes wrong (done)

\- Figuring out why mmseqs2 would have issues such as file correputped, this should not be the case as we are comparing sequences, be prepared to answer this question

\- Complete the script for pickle file downloading, give a found list and list not found





https://github.com/KosinskiLab/AlphaPulldown?tab=readme-ov-file#features-database

12. pickle file downloading:

\- a python sciprt to compare existing protein sequences

\- generate a bash script for pickle downloading

bash script complete

pkill -9 -f "download_found.sh"



Download to current directory:

mc cp embl/alphapulldown/input_features/Saccharomyces_cerevisiae/Q01329.pkl.xz .



Download to specific directory:

mc cp embl/alphapulldown/input_features/Saccharomyces_cerevisiae/Q01329.pkl.xz /data7/Conny/data/FeaturePickleDB/



Command to perform download while storing the output

bash download_found.sh | tee download_output.log



Decompress all of the xz files while keeping the original

xz -dk *.xz



13. Investigate why MMseq2 would encounter issue

scp /Users/conny/Desktop/AlphaFold/test_sequence.fasta jzho349@kilimanjaro.biochem.emory.edu:/data7/Conny/data





NUM_SEQ=$(grep -c "^>" example_1_sequences.fasta)



for ((i=0; i<$NUM_SEQ; i++)); do

 echo "Processing sequence index $i"

 python /path/to/sbgrid/create_individual_features.py \

  --fasta_paths=example_1_sequences.fasta \

  --data_dir="$DATA_DIR" \

  --output_dir="$OUTPUT_DIR" \

  --skip_existing=True \

  --use_mmseqs2=True \

  --max_template_date="2050-01-01" \

  --seq_index=$i || echo "[WARN] Failed to process sequence $i"

done



































\- APD is a customized implementation of AFM



\- Overview, 3 steps

1. Create and store MSA and template features (CPU only) by searching a preinstalled databases, and calculating the MSA for all found homologs.

\- MMSeq2 speeds up

\- This step uses the alphafold database, and generate features for each protein sequence though I am not sure what these features are 

2. NN, GPU required