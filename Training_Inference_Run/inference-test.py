from argparse import ArgumentParser
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
import deepspeed
import math
import os
import torch
import time
from utils import DSPipeline
from deepspeed.runtime.utils import see_memory_usage
import subprocess

#os.environ["CUDA_VISIBLE_DEVICES"] = "1,2,3,0"
#os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
parser = ArgumentParser()

parser.add_argument("--name", required=True, type=str, help="model_name")
parser.add_argument("--checkpoint_path", required=False, default=None, type=str, help="model checkpoint path")
parser.add_argument("--save_mp_checkpoint_path", required=False, default=None, type=str, help="save-path to store the new model checkpoint")
parser.add_argument("--batch_size", default=1, type=int, help="batch size")
parser.add_argument("--dtype", default="float16", type=str, choices=["float32", "float16", "int8"], help="data-type")
parser.add_argument("--ds_inference", action='store_true', help="enable ds-inference")
parser.add_argument("--use_kernel", action='store_true', help="enable kernel-injection")
parser.add_argument("--max_tokens", default=1024, type=int, help="maximum tokens used for the text-generation KV-cache")
parser.add_argument("--max_new_tokens", default=50, type=int, help="maximum new tokens to generate")
parser.add_argument("--greedy", action='store_true', help="greedy generation mode")
parser.add_argument("--use_meta_tensor", action='store_true', help="use the meta tensors to initialize model")
parser.add_argument("--use_cache", default=True, type=bool, help="use cache for generation")
parser.add_argument("--local_rank", type=int, default=0, help="local rank")
parser.add_argument("--mp", type=int, default=30000, help="master port")
args = parser.parse_args()

os.environ['MASTER_PORT'] = str(args.mp)
world_size = int(os.getenv('WORLD_SIZE', '1'))
#local_rank = int(os.getenv('LOCAL_RANK', '0'))
local_rank = int(os.getenv("LOCAL_RANK", args.local_rank))
torch.cuda.set_device(local_rank)
device = torch.device("cuda", local_rank) if torch.cuda.is_available() else torch.device("cpu")


data_type = getattr(torch, args.dtype)

if local_rank == 0:
    see_memory_usage("before init", True)

#Generating GPU Statistics Report
#subprocess.Popen("nvidia-smi --query-gpu=timestamp,name,pstate,gpu_bus_id,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv -lms 250 > ./nvidia.log", shell=True)
t0 = time.time()
pipe = DSPipeline(model_name=args.name,
                  dtype=data_type,
                  is_meta=args.use_meta_tensor,
                  device=device,
                  checkpoint_path=args.checkpoint_path)
t1=time.time()
print(f'DSPipeline process time is {t1-t0} sec')

if local_rank == 0:
    print(f"initialization time: {(time.time()-t0) * 1000}ms")
    see_memory_usage("after init", True)
if args.use_meta_tensor:
    ds_kwargs = dict(base_dir=pipe.repo_root, checkpoint=pipe.checkpoints_json)
else:
    ds_kwargs = dict()

if args.ds_inference:
    pipe.model = deepspeed.init_inference(pipe.model,
                                    dtype=data_type,
                                    mp_size=world_size,
                                    replace_with_kernel_inject=True, #args.use_kernel,
                                    replace_method='auto',
                                    max_tokens=args.max_tokens,
                                    save_mp_checkpoint_path=args.save_mp_checkpoint_path,
                                    **ds_kwargs
                                    )
print(f'deepspeed.init_inference process time is {time.time()-t1} sec')
if local_rank == 0:
    see_memory_usage("after init_inference", True)


input_sentences = [
         "DeepSpeed is a machine learning framework",
         "He is working on",
         "He has a",
         "He got all",
         "Everyone is happy and I can",
         "The new movie that got Oscar this year",
         "In the far far distance from our galaxy,",
         "Peace is the only way"
]

if args.batch_size > len(input_sentences):
    # dynamically extend to support larger bs by repetition
    input_sentences *= math.ceil(args.batch_size / len(input_sentences))

inputs = input_sentences[:args.batch_size]

# warmup
outputs = pipe(inputs,
              num_tokens=args.max_new_tokens,
              do_sample=(not args.greedy))

torch.cuda.synchronize()
start = time.time()

outputs = pipe(inputs,
              num_tokens=args.max_new_tokens,
              do_sample=(not args.greedy))

torch.cuda.synchronize()
end = time.time()
print(f'generation time is {end-start} sec')

###subprocess.Popen("pkill -9 nvidia-smi", shell=True)

if args.local_rank == 0:
    for i, o in zip(inputs, outputs):
        print(f"\nin={i}\nout={o}\n{'-'*60}")

print(f'Total time is {end-t0} sec')
