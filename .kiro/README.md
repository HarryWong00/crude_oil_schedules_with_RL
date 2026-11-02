# .kiro

Agent / Specs / Hooks 配置目录。

| 文件 | 对应 | 作用 |
|---|---|---|
| `agents.json` | Agent | 三个协作角色的职责、作用文件、接口与护栏（env / train / eval） |
| `specs.yaml` | Specs | 规格索引：每个 spec 的目标、代码入口、验收条件、状态 |
| `hooks.py` | Hooks | 可执行钩子：提交前语法检查、训练产物拦截、JSON/YAML 校验 |
| `steering/project.md` | — | 项目约定，会话启动时自动加载 |

## 自检

```bash
python .kiro/hooks.py pre-commit    # 检查已 staged 的改动
python .kiro/hooks.py install       # 安装为 .git/hooks/pre-commit
python .kiro/hooks.py check-all     # 不依赖 git 状态的全仓语法体检
```

`hooks.py` 只依赖 Python 标准库，不需要额外安装。
