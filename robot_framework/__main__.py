"""The entry point of the process."""

# Remember to delete this error
raise NotImplementedError("Remember to choose a framework to use.")

# Framework to build
#   Load OrchestratorConnection here with args
#   Run one of two processes based on args
#       1.  Upload queue
#           Looks into sql database and checks which patients should be processed
#           Uploads those patients to the Orchestrator database
#           (Probably a linear framework)
#       2.  Handle queue
#           Processes the patients selected from the sql database
#           (Defintely a queue framework)

# from robot_framework import linear_framework
# linear_framework.main()

# from robot_framework import queue_framework
# queue_framework.main()
