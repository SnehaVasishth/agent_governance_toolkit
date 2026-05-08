from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from agent_control_plane import KernelSpace, PolicyEngine, SyscallType
import os
import asyncio
from dotenv import load_dotenv

def web_search(query:str)->str:
    return f"Mock google search for {query}"

def read_file(path:str)->str:
    with open(path,'r') as f:
        return f.read()
        
async def main():
    load_dotenv()
    agent_id='sneha1'
    client=OpenAIChatClient(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
        api_key=os.getenv("OPENAI_KEY"),
        base_url="https://api.openai.com/v1"
    )
    
    agent=Agent(
        client=client,
        name="MyAgent",
        instructions="You are a helpful assistant. Keep answers concise."
    )
    policy= PolicyEngine()
    policy.add_constraint(
        role=agent_id,
        allowed_tools=["chat","web_search","read_file"]
    )
    policy.freeze()
    kernel=KernelSpace(policy_engine=policy)
    ctx=kernel.create_agent_context(agent_id)
    kernel.register_tool("web_search",web_search)
    kernel.register_tool("read_file",read_file)

    # check_run= await ctx.syscall(
    #     SyscallType.SYS_EXEC,
    #     tool="chat",
    #     args={"prompt":"what are agent governance means"}
    # )
    # if not check_run.success or not check_run.return_value.get("allowed",False):
    #     raise RuntimeError(f"chat blocked :{check_run.return_value}")
    

    # print("\n chat run \n",check_run.return_value)
    
    # tool_check=await ctx.syscall(
    #     SyscallType.SYS_CHECKPOLICY,
    #     action="web_search",
    #     args={"query":"OWASP 10 "}
    # )
    # if not tool_check.success or not tool_check.return_value.get("allowed",False):
    #     raise RuntimeError(f"tool blocked :{tool_check.return_value}")
    
    violation= policy.check_violation(
        agent_id,
        "chat",
        {"prompt":"what are agent governance"}
    )
    if violation:
        raise PermissionError(f"blocked run :{violation}")
    
    res= await agent.run("what are agent governance")
    print("output of run \n",res)
    
    exec_tool=await ctx.syscall(
        SyscallType.SYS_EXEC,
        tool="web_search",
        args={"query":"OWASP top 10 for agentic applications 2026"}
    )
    if not exec_tool.success:
        raise RuntimeError(exec_tool.error_message)
    print("\n tool result \n",exec_tool.return_value)
    
    blocked= await ctx.syscall(
        SyscallType.SYS_EXEC,
        tool='delete_file',
        args={"path":r"C:\Users\Sneha\Downloads"}
        
    )
    print("\n blocked action ",blocked.return_value)
if __name__ == '__main__':
    asyncio.run(main())
