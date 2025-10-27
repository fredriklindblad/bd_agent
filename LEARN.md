PydanticAI
"""hur agenten fungerar, dvs tolkning av result.all_messages()"""
# 1. ModelRequest:  agenten skickar user prompt och systm prompt tsm med tillg tool info
# 2. ModelResponse: LLM svarar med text som innehåller tool call, anropar tool
# 2b. ToolCallPart: innehåller tool name och args som LLM bestämt
# 3. ModelRequest:  agenten anropar tool med args och skickar svar till LLM
# 4. ModelResponse: LLM svarar med ToolCallPart, vill anropa tool igen
# 5. ModelRequest:  agenten anropar tool med args och skickar svar till LLM
# 6. ModelResponse: LLM kallar på output tool och fyller enligt output typ
# 7. ModelRequest: output funktionen körs i Python och "Final result processed." returneras
#
#

""" hur agenten fungerar vad gäller användade av tools """
# 1a. om jag skriver i system prompt "får inte" använda tool_1 så används det inte
# 1b. om jag skriver "måste" använda tool_1 så används det
# 2. annat som LLM tittar på när d3et avgör om tool ska användas
#   a. namn på tool
#   b. doc string i tool
#   c. output type i tool (hjälper det för agentens output type så använder gärna)
#   d. cost för att anropa, är det en tung eller lätt funktion?