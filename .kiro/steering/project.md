# 项目约定（Kiro steering）

## 仓库形态
每个 `NN-ALGO-MMDD-配置` 目录是一次独立实验，内含 `env.py`（环境）、`PPO.py`（算法）、
`train.py` / `test.py` / `run.py`（流程）、`PPO_logs` 与 `PPO_preTrained`（产物）。

## 三条硬规则
1. **历史 run 只读**：已存在的实验目录不修改，新想法开新目录，命名沿用 `NN-ALGO-MMDD-关键改动`。
2. **状态维度不变式**：`Env.reset()` 返回 14 维（3 塔完成率 + 10 罐液位 + 当前时间）。
   动环境前先确认这条，动了就同步更新 `.kiro/specs.yaml` 的 `env-core`。
3. **产物不入库**：`PPO_preTrained/*.pth`、`PPO_logs/*`、`__pycache__` 一律本地保留。
   `.kiro/hooks.py pre-commit` 会拦截。

## 动作空间
动作解码顺序固定为「选塔 → 选罐 → 给速率」，对应 `selectDistiller` → `selectTank` → `charge`。
任何一步非法都返回空选择，不得靠异常中断 episode。

## 提交前
```
python .kiro/hooks.py pre-commit     # 语法 + 大文件 + 元数据
python .kiro/hooks.py install        # 装成 git 钩子（可选，一次即可）
```
