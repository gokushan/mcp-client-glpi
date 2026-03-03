#!/bin/bash
echo "INICIO: $(date '+%D %H:%M:%S')"; curl -X POST http://localhost:8000/processcontract; echo -e "\nFIN:    $(date '+%D %H:%M:%S')"
