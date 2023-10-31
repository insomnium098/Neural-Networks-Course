# Neural-Networks-Course
Final project for the Neural Networks Curse


## DeepSlide

### Requisitos:

Instalar conda en su distro. 

[Windows](https://conda.io/projects/conda/en/latest/user-guide/install/windows.html)

[Linux](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)

**Dependencias**

```
conda env create --file setup/conda_env.yaml
```

**OpenSlide**

En linux, ejecutar `./setup/install_openslide.sh`

Para Windows, o si desconfían del script:

[OpenSlide](https://openslide.org/download/)

### Configuración

La configuración se realiza en el archivo `code/config.py`

Modificaciones:

* Reducción de 8 a 4 hilos (línea 58).
* Reducción del número de *Training patches per class* de `8000` a `1000` (línea 136).

**Set de Imágenes**

Todas las imágenes a testear se deben ingresar en `all_wsi/a` o `all_wsi/b`. 
Los nombres `a` y `b` son arbitrarios y podrían cambiarse a algo como `con_cancer` y `sin_cancer` o algo así. 
El script usa estos directorios para entrenarse. 

### Ejecución 

La ejecución se compone de 7 pasos, o pueden hacer la [ejecución rápida](#ejecución-rápida) si ya están seguros de los parámetros adicionales que modificaron en `config.py`.
Cada paso consta de ciertos `inputs` y `outputs`.
Es recomendable eliminar los outputs que ya están para no contaminar la prueba. 
Para más detalles dirigirse al [README](deepslide/README.md) fuente.

#### 1. Split Train-Val-Test

**Inputs**

`all_wsi`

**Outputs**

`wsi_train`, `wsi_val`, `wsi_test`, `labels_train.csv`, `labels_val.csv`, `labels_test.csv`

 Por defecto, la validación de imágenes de diapositivas completas (WSI) por clase es de 20 e imágenes de prueba por clase es de 30. 
 Pueden cambiar estos números modificando los indicadores `--val_wsi_per_class` y `--test_wsi_per_class` en tiempo de ejecución.

**Ejemplo**

`python code/1_split.py --val_wsi_per_class 5 --test_wsi_per_class 10`

#### 2. Data Processing

Inputs: `wsi_train`, `wsi_val`, `wsi_test`

Outputs: `train_folder`, `patches_eval_train`, `patches_eval_test` 

**Ejemplo**

`python code/2_process_patches.py --slide_overlap 2`

#### 3. Model Training

Inputs: `train_folder`

Outputs: `checkpoints`, `logs`

**Ejemplo**

`CUDA_VISIBLE_DEVICES=0 python code/3_train.py --batch_size 32 --num_epochs 100 --save_interval 5`

#### 4. Testing on WSI

Inputs: `patches_eval_val`, `patches_eval_test`

Outputs: `preds_val`, `preds_test`

**Ejemplo**

`CUDA_VISIBLE_DEVICES=0 python code/4_test.py --auto_select False`

#### 5. Searching for Best Thresholds

Inputs: `preds_val`, `labels_val.csv`

Outputs: `inference_val`

**Ejemplo**

`python code/5_grid_search.py --preds_val different_labels_val.csv`

#### 6. Visualization

Inputs: `wsi_val`, `preds_val`

Outputs: `vis_val`

**Ejemplo**

`python code/6_visualize.py --vis_test different_vis_test_directory`

#### 7. Final Testing

Inputs: `preds_test`, `labels_test.csv`, `inference_val` , `labels_val` 

Outputs: `inference_test` 

**Ejemplo**

`python code/7_final_test.py --labels_test different_labels_test.csv`

### Ejecución Rápida

`sh code/run_all.sh`

