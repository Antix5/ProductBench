# Benchmark Results

| Model | Scenario | Params | Total Cost ($) | Label Aug Score | Rerank Dist | Aug Cost/Item ($) | Rerank Cost/Item ($) | Time (s) | Note |
|---|---|---|---|---|---|---|---|---|---|
| Gemini 3 flash (Judge) | shelf_category | Unknown | $0.035598 | 0.9121 | 0.0040 | $0.000212 | $0.000127 | 29.30 | This model is here to see how the judge model self evaluate. |
| Gemini 3.1 Flash Lite Preview | shelf_category | Unknown | $0.014444 | 0.8818 | 0.2893 | $0.000102 | $0.000017 | 25.81 |  |
| Gemini 2.5 Flash | shelf_category | Unknown | $0.022652 | 0.8758 | 0.0051 | $0.000132 | $0.000087 | 18.48 | Google's state-of-the-art workhorse model, specifically designed for advanced reasoning, coding, mathematics, and scientific tasks. |
| Kimi k2 0905 | shelf_category | 1T | $0.026492 | 0.8273 | 0.0079 | $0.000160 | $0.000090 | 33.48 |  |
| Gemini 2.0 flash | shelf_category | Unknown | $0.006546 | 0.8227 | 0.0046 | $0.000039 | $0.000022 | 12.45 | Google's Gemini 2 Flash model. Reference model |
| Kimi K2.5 | shelf_category | 1T | $0.040331 | 0.8182 | 0.0046 | $0.000237 | $0.000151 | 24.95 |  |
| Gemini 2.5 Flash lite | shelf_category | Unknown | $0.006563 | 0.7924 | 0.0070 | $0.000040 | $0.000022 | 10.15 |  |
| Mistral Large 3 2512 | shelf_category | 675B MOE | $0.033750 | 0.7780 | 0.0040 | $0.000207 | $0.000106 | 17.09 |  |
| Deepseek V3.2 | shelf_category | 600B | $0.014742 | 0.7773 | 0.0019 | $0.000090 | $0.000047 | 26.18 |  |
| Kat Coder Pro | shelf_category | Unknown | $0.014120 | 0.7402 | 0.0120 | $0.000084 | $0.000050 | 31.13 |  |
| Mimo V2 Flash | shelf_category | 300B | $0.000000 | 0.7114 | 0.0066 | $0.000000 | $0.000000 | 46.57 |  |
| Hermes 4 70B | shelf_category | 70B | $0.007166 | 0.6712 | 0.0080 | $0.000043 | $0.000025 | 11.81 |  |
| Qwen 3.5 Flash 02-23 | shelf_category | Unknown | $0.006966 | 0.6629 | 0.0104 | $0.000042 | $0.000024 | 23.62 |  |
| Google Gemma 3 12B Instruct | shelf_category | 12B | $0.002012 | 0.6508 | 0.0088 | $0.000012 | $0.000007 | 13.94 |  |
| Mistral Small 3 | shelf_category | 24B | $0.002732 | 0.6258 | 0.0079 | $0.000018 | $0.000007 | 18.81 |  |
| Ministral 14B 2512 | shelf_category | 14B | $0.012418 | 0.6053 | 0.0300 | $0.000078 | $0.000036 | 12.69 |  |
| Seed 2.0 Mini | shelf_category | Unknown | $0.008172 | 0.5970 | 0.0224 | $0.000050 | $0.000026 | 29.58 |  |
| Microsoft Phi-4 | shelf_category | 14B | $0.003690 | 0.5917 | 0.0079 | $0.000022 | $0.000012 | 14.07 |  |
| Ministral 8B 2512 | shelf_category | 14B | $0.009298 | 0.5818 | 0.0340 | $0.000058 | $0.000027 | 11.14 |  |
| Amazon Nova Micro 1.0 | shelf_category | Unknown (Micro) | $0.002322 | 0.5803 | 0.0264 | $0.000014 | $0.000008 | 13.18 |  |
| Cohere Command R7B | shelf_category | 7B | $0.002622 | 0.5500 | 0.0275 | $0.000015 | $0.000012 | 12.54 |  |
| Mistral Nemo 12B | shelf_category | 12B | $0.001272 | 0.5417 | 0.0222 | $0.000008 | $0.000004 | 15.96 |  |
| Gemini 2.5 Flash Lite Preview | shelf_category | Unknown | $0.006584 | 0.5292 | 0.0032 | $0.000040 | $0.000022 | 21.45 |  |
| Ministral 3B 2512 | shelf_category | 14B | $0.006152 | 0.5189 | 0.0364 | $0.000039 | $0.000018 | 11.76 |  |
| Google Gemma 3 4B Instruct | shelf_category | 4B | $0.001157 | 0.4886 | 0.0364 | $0.000007 | $0.000004 | 11.80 |  |
| Mistral Ministral 3B | shelf_category | 3B | $0.002440 | 0.4394 | 0.0558 | $0.000015 | $0.000007 | 9.03 |  |
| GPT-4.1 Nano | shelf_category | Unknown | $0.006457 | 0.4174 | 0.0116 | $0.000038 | $0.000023 | 17.49 |  |
| Liquid LFM 2 24B A2B | shelf_category | 24B | $0.002127 | 0.3992 | 0.0521 | $0.000013 | $0.000008 | 17.08 |  |
| Llama 3.3 70B Instruct | shelf_category | 70B | $0.006503 | 0.2864 | 0.0067 | $0.000039 | $0.000023 | 25.38 |  |
| Llama 3.3 Nemotron Super 49B v1.5 | shelf_category | 7B | $0.006770 | 0.2555 | 0.0187 | $0.000040 | $0.000025 | 18.62 |  |
| Mistral Small Creative | shelf_category | 24B | $0.006758 | 0.1747 | 0.0266 | $0.000041 | $0.000021 | 23.42 |  |
| GPT-4o Mini | shelf_category | Unknown | $0.009589 | 0.0886 | 0.0053 | $0.000057 | $0.000034 | 22.37 |  |
| Olmo 3.1 32B Instruct | shelf_category | 32B | $0.012619 | 0.0382 | 0.0393 | $0.000076 | $0.000043 | 18.74 |  |
| GPT OSS 20B | shelf_category | 20B | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 8.15 |  |
| GPT OSS 120B | shelf_category | 120B | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 7.13 |  |
| GPT-5 Nano | shelf_category | Unknown | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 6.68 |  |
| GPT-5 Mini | shelf_category | Unknown | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 6.62 |  |
| Gemini 3 flash (Judge) | product_type | Unknown | $0.035574 | 0.8818 | 0.0027 | $0.000212 | $0.000127 | 15.38 | This model is here to see how the judge model self evaluate. |
| Gemini 3.1 Flash Lite Preview | product_type | Unknown | $0.017144 | 0.8636 | 0.0074 | $0.000102 | $0.000062 | 22.62 |  |
| Gemini 2.5 Flash | product_type | Unknown | $0.022633 | 0.8485 | 0.0056 | $0.000132 | $0.000087 | 12.47 | Google's state-of-the-art workhorse model, specifically designed for advanced reasoning, coding, mathematics, and scientific tasks. |
| Gemini 2.0 flash | product_type | Unknown | $0.006554 | 0.8129 | 0.0090 | $0.000040 | $0.000022 | 14.01 | Google's Gemini 2 Flash model. Reference model |
| Kimi K2.5 | product_type | 1T | $0.040256 | 0.7758 | 0.0046 | $0.000237 | $0.000151 | 29.48 |  |
| Kimi k2 0905 | product_type | 1T | $0.026771 | 0.7568 | 0.0079 | $0.000158 | $0.000098 | 23.10 |  |
| Gemini 2.5 Flash lite | product_type | Unknown | $0.006567 | 0.7273 | 0.0070 | $0.000040 | $0.000022 | 10.69 |  |
| Mistral Large 3 2512 | product_type | 675B MOE | $0.033724 | 0.7144 | 0.0067 | $0.000207 | $0.000106 | 16.22 |  |
| Deepseek V3.2 | product_type | 600B | $0.014710 | 0.6909 | 0.0032 | $0.000090 | $0.000047 | 25.65 |  |
| Gemini 2.5 Flash Lite Preview | product_type | Unknown | $0.006587 | 0.6641 | 0.0059 | $0.000040 | $0.000022 | 29.68 |  |
| Kat Coder Pro | product_type | Unknown | $0.014067 | 0.6485 | 0.0106 | $0.000084 | $0.000050 | 28.06 |  |
| Hermes 4 70B | product_type | 70B | $0.007151 | 0.6341 | 0.0094 | $0.000043 | $0.000025 | 11.23 |  |
| Seed 2.0 Mini | product_type | Unknown | $0.009076 | 0.6311 | 0.0158 | $0.000057 | $0.000026 | 26.91 |  |
| Mimo V2 Flash | product_type | 300B | $0.000000 | 0.6258 | 0.0114 | $0.000000 | $0.000000 | 48.90 |  |
| Qwen 3.5 Flash 02-23 | product_type | Unknown | $0.006814 | 0.6197 | 0.0046 | $0.000041 | $0.000024 | 29.11 |  |
| Google Gemma 3 12B Instruct | product_type | 12B | $0.002016 | 0.5659 | 0.0144 | $0.000012 | $0.000007 | 14.86 |  |
| Mistral Small 3 | product_type | 24B | $0.002985 | 0.5561 | 0.0093 | $0.000020 | $0.000007 | 20.62 |  |
| Mistral Small Creative | product_type | 24B | $0.006757 | 0.5561 | 0.0212 | $0.000041 | $0.000021 | 24.90 |  |
| Mistral Nemo 12B | product_type | 12B | $0.001271 | 0.5417 | 0.0301 | $0.000008 | $0.000004 | 13.87 |  |
| Ministral 8B 2512 | product_type | 14B | $0.009284 | 0.5174 | 0.0289 | $0.000058 | $0.000027 | 9.86 |  |
| Cohere Command R7B | product_type | 7B | $0.002671 | 0.5068 | 0.0295 | $0.000015 | $0.000012 | 13.31 |  |
| Amazon Nova Micro 1.0 | product_type | Unknown (Micro) | $0.002312 | 0.5053 | 0.0303 | $0.000014 | $0.000008 | 15.76 |  |
| Microsoft Phi-4 | product_type | 14B | $0.003687 | 0.4992 | 0.0086 | $0.000022 | $0.000013 | 16.42 |  |
| Ministral 14B 2512 | product_type | 14B | $0.012369 | 0.4674 | 0.0243 | $0.000077 | $0.000036 | 11.09 |  |
| GPT-4o Mini | product_type | Unknown | $0.009578 | 0.4668 | 0.0066 | $0.000057 | $0.000034 | 18.58 |  |
| Google Gemma 3 4B Instruct | product_type | 4B | $0.001156 | 0.4030 | 0.0396 | $0.000007 | $0.000004 | 11.97 |  |
| Olmo 3.1 32B Instruct | product_type | 32B | $0.012618 | 0.3788 | 0.0342 | $0.000076 | $0.000043 | 14.02 |  |
| Llama 3.3 Nemotron Super 49B v1.5 | product_type | 7B | $0.006766 | 0.3785 | 0.0187 | $0.000040 | $0.000025 | 17.70 |  |
| Mistral Ministral 3B | product_type | 3B | $0.002439 | 0.3720 | 0.0714 | $0.000015 | $0.000007 | 13.83 |  |
| Ministral 3B 2512 | product_type | 14B | $0.006149 | 0.3621 | 0.0328 | $0.000039 | $0.000018 | 11.45 |  |
| Llama 3.3 70B Instruct | product_type | 70B | $0.006505 | 0.2904 | 0.0067 | $0.000039 | $0.000023 | 21.23 |  |
| GPT-4.1 Nano | product_type | Unknown | $0.006443 | 0.2513 | 0.0110 | $0.000038 | $0.000023 | 17.51 |  |
| Liquid LFM 2 24B A2B | product_type | 24B | $0.002127 | 0.1155 | 0.0467 | $0.000013 | $0.000008 | 20.50 |  |
| GPT OSS 20B | product_type | 20B | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 8.39 |  |
| GPT OSS 120B | product_type | 120B | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 6.86 |  |
| GPT-5 Nano | product_type | Unknown | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 6.98 |  |
| GPT-5 Mini | product_type | Unknown | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 7.16 |  |
| Gemini 3 flash (Judge) | base | Unknown | $0.035058 | 0.8750 | 0.0040 | $0.000209 | $0.000125 | 15.87 | This model is here to see how the judge model self evaluate. |
| Gemini 3.1 Flash Lite Preview | base | Unknown | $0.016849 | 0.7992 | 0.0074 | $0.000100 | $0.000061 | 23.81 |  |
| Gemini 2.5 Flash | base | Unknown | $0.022282 | 0.7750 | 0.0075 | $0.000130 | $0.000086 | 12.64 | Google's state-of-the-art workhorse model, specifically designed for advanced reasoning, coding, mathematics, and scientific tasks. |
| Gemini 2.0 flash | base | Unknown | $0.006484 | 0.7356 | 0.0042 | $0.000039 | $0.000022 | 12.19 | Google's Gemini 2 Flash model. Reference model |
| Kimi K2.5 | base | 1T | $0.039544 | 0.7318 | 0.0040 | $0.000232 | $0.000148 | 22.80 |  |
| Kimi k2 0905 | base | 1T | $0.026040 | 0.6856 | 0.0114 | $0.000155 | $0.000093 | 18.80 |  |
| Mistral Large 3 2512 | base | 675B MOE | $0.033118 | 0.6629 | 0.0046 | $0.000204 | $0.000104 | 18.81 |  |
| Deepseek V3.2 | base | 600B | $0.014517 | 0.6576 | 0.0019 | $0.000089 | $0.000046 | 28.34 |  |
| Gemini 2.5 Flash lite | base | Unknown | $0.006451 | 0.6439 | 0.0070 | $0.000039 | $0.000022 | 10.57 |  |
| Gemini 2.5 Flash Lite Preview | base | Unknown | $0.006480 | 0.6303 | 0.0046 | $0.000039 | $0.000022 | 12.91 |  |
| Kat Coder Pro | base | Unknown | $0.013885 | 0.6076 | 0.0108 | $0.000083 | $0.000048 | 38.47 |  |
| Mimo V2 Flash | base | 300B | $0.000000 | 0.5818 | 0.0105 | $0.000000 | $0.000000 | 72.23 |  |
| GPT-4o Mini | base | Unknown | $0.009417 | 0.5727 | 0.0064 | $0.000056 | $0.000034 | 15.61 |  |
| Qwen 3.5 Flash 02-23 | base | Unknown | $0.006356 | 0.5417 | 0.1231 | $0.000041 | $0.000016 | 21.90 |  |
| Hermes 4 70B | base | 70B | $0.007042 | 0.5182 | 0.0096 | $0.000042 | $0.000025 | 11.93 |  |
| Mistral Small 3 | base | 24B | $0.003581 | 0.4992 | 0.0066 | $0.000024 | $0.000006 | 27.45 |  |
| Seed 2.0 Mini | base | Unknown | $0.008996 | 0.4932 | 0.0211 | $0.000056 | $0.000026 | 28.29 |  |
| Mistral Small Creative | base | 24B | $0.006639 | 0.4773 | 0.0172 | $0.000041 | $0.000021 | 17.24 |  |
| Llama 3.3 Nemotron Super 49B v1.5 | base | 7B | $0.006655 | 0.4485 | 0.0195 | $0.000039 | $0.000024 | 14.82 |  |
| Microsoft Phi-4 | base | 14B | $0.003621 | 0.4364 | 0.0086 | $0.000022 | $0.000012 | 14.61 |  |
| GPT-4.1 Nano | base | Unknown | $0.006373 | 0.4333 | 0.0116 | $0.000038 | $0.000023 | 19.05 |  |
| Amazon Nova Micro 1.0 | base | Unknown (Micro) | $0.002265 | 0.4265 | 0.0287 | $0.000014 | $0.000008 | 13.64 |  |
| Google Gemma 3 12B Instruct | base | 12B | $0.001978 | 0.4212 | 0.0130 | $0.000012 | $0.000007 | 15.78 |  |
| Mistral Nemo 12B | base | 12B | $0.001256 | 0.4182 | 0.0456 | $0.000008 | $0.000004 | 17.20 |  |
| Ministral 8B 2512 | base | 14B | $0.009110 | 0.4038 | 0.0350 | $0.000057 | $0.000026 | 10.45 |  |
| Llama 3.3 70B Instruct | base | 70B | $0.006384 | 0.3864 | 0.0101 | $0.000038 | $0.000022 | 18.39 |  |
| Ministral 14B 2512 | base | 14B | $0.012180 | 0.3841 | 0.0456 | $0.000076 | $0.000035 | 9.56 |  |
| Cohere Command R7B | base | 7B | $0.002604 | 0.3720 | 0.0288 | $0.000014 | $0.000012 | 12.99 |  |
| Google Gemma 3 4B Instruct | base | 4B | $0.001146 | 0.3477 | 0.0317 | $0.000007 | $0.000004 | 11.74 |  |
| Olmo 3.1 32B Instruct | base | 32B | $0.012418 | 0.3341 | 0.0410 | $0.000075 | $0.000042 | 14.06 |  |
| Ministral 3B 2512 | base | 14B | $0.006044 | 0.2977 | 0.0250 | $0.000038 | $0.000017 | 11.91 |  |
| Liquid LFM 2 24B A2B | base | 24B | $0.002092 | 0.2939 | 0.0522 | $0.000013 | $0.000007 | 17.00 |  |
| Mistral Ministral 3B | base | 3B | $0.002396 | 0.2545 | 0.0590 | $0.000015 | $0.000007 | 9.25 |  |
| GPT OSS 20B | base | 20B | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 8.09 |  |
| GPT OSS 120B | base | 120B | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 7.14 |  |
| GPT-5 Nano | base | Unknown | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 6.67 |  |
| GPT-5 Mini | base | Unknown | $0.000000 | 0.0076 | 0.4089 | $0.000000 | $0.000000 | 6.68 |  |
