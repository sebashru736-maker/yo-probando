"""SRVGG architecture from Xintao Wang's Real-ESRGAN (BSD-3-Clause)."""
from torch import nn
from torch.nn import functional as F
import torch,numpy as np,cv2

class SRVGGNetCompact(nn.Module):
 def __init__(self,num_conv=32):
  super().__init__();self.body=nn.ModuleList([nn.Conv2d(3,64,3,1,1),nn.PReLU(64)])
  for _ in range(num_conv):self.body.extend([nn.Conv2d(64,64,3,1,1),nn.PReLU(64)])
  self.body.append(nn.Conv2d(64,48,3,1,1));self.upsampler=nn.PixelShuffle(4)
 def forward(self,x):
  out=x
  for m in self.body:out=m(out)
  return self.upsampler(out)+F.interpolate(x,scale_factor=4,mode='nearest')

def model(animation=False):
 torch.set_num_threads(3)
 m=SRVGGNetCompact(16 if animation else 32).eval()
 name='realesr-animevideov3.pth' if animation else 'realesr-general-x4v3.pth'
 data=torch.load('/workspace/creative-tools/models/'+name,map_location='cpu',weights_only=True)
 m.load_state_dict(data['params']);return m.to(memory_format=torch.channels_last)

@torch.inference_mode()
def upscale(m,bgr):
 x=torch.from_numpy(np.ascontiguousarray(bgr[:,:,::-1])).permute(2,0,1).unsqueeze(0).float()/255
 x=x.contiguous(memory_format=torch.channels_last)
 # BF16 uses the CPU's native vector kernels; convert to float32 for output.
 with torch.autocast('cpu',dtype=torch.bfloat16):y=m(x)
 y=y.float().squeeze(0).clamp(0,1).permute(1,2,0).numpy()
 return np.round(y[:,:,::-1]*255).astype(np.uint8)
