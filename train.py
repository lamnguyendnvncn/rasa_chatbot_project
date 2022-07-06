import neptune.new as neptune
import os
import sys
from distutils.util import strtobool
run = neptune.init(
    project="intern-1/Rasa-001",
    api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiJiZTM2MzQ4ZC05OTA5LTRiMGYtYTRiMy05NTIzODdmNzVjZGIifQ=="
)  

run["artifacts/result"].upload_files("rasa_init")

# def train_model(app_name: str, config="config.yml", training_files="data/", domain="domain.yml", output="models/"):
#     """Run `rasa train`"""
#     import rasa

#     print(config, training_files, domain, output)

#     # apps not using intent_classification have some problems with
#     can_incremental_training = app_name not in ["job_search", "zipcode"]
#     incremental_training: int = strtobool(os.environ.get("INCREMENTAL_TRAINING", "false"))
#     incremental_training = incremental_training if can_incremental_training else False
#     finetune_model_path = None

#     if incremental_training:
#         incremental_training, finetune_model_path = verify_model_incremental_training_config(app_name)

#     if incremental_training and finetune_model_path:
#         print("FINE-TUNING MODEL")
#         model_path = rasa.train(
#             domain,
#             config,
#             [training_files],
#             output,
#             model_to_finetune=finetune_model_path,
#             finetuning_epoch_fraction=0.2  # train with 20% of default epochs
#         )
#     else:
#         if can_incremental_training:
#             # apply incremental training config to have this option valid for the next training times
#             apply_incremental_training_config(config)
#         model_path = rasa.train(domain, config, [training_files], output)

#     return model_path, incremental_training