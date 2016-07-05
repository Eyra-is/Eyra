# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Matthias Petursson <oldschool01123@gmail.com>

# can use this to stop (but not terminate, use -SIGTERM for that), i.e. pause, decoding of graphs issued by genGraphs.sh
# by commenting out here, ses also intermediate_decoding.sh to continue
ps aux | grep graph_gen_aa  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ab  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ac  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ad  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ae  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_af  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ag  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ah  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ai  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_aj  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ak  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_al  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_am  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_an  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ao  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ap  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_aq  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ar  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_as  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_at  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_au  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_av  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_aw  | awk '{print $2}' | xargs kill -SIGSTOP;
ps aux | grep graph_gen_ax  | awk '{print $2}' | xargs kill -SIGSTOP;
