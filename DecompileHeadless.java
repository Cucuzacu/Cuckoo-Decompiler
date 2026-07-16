// DecompileHeadless.java
// part of the Cuckoo-Decompiler project

import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.decompiler.DecompiledFunction;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.util.task.ConsoleTaskMonitor;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Set;
import java.util.HashSet;

public class DecompileHeadless extends GhidraScript {
    
    private static final Set<String> BOILERPLATE_NAMES = new HashSet<>();
    static {
        BOILERPLATE_NAMES.add("entry");
        BOILERPLATE_NAMES.add("pre_c_initialization");
        BOILERPLATE_NAMES.add("post_p_initialization");
        BOILERPLATE_NAMES.add("_find_pe_section");
        BOILERPLATE_NAMES.add("__security_init_cookie");
        BOILERPLATE_NAMES.add("__scrt_common_main_seh");
        BOILERPLATE_NAMES.add("_mainCRTStartup");
        BOILERPLATE_NAMES.add("__report_gsfailure");
        BOILERPLATE_NAMES.add("_crt_atexit");
        BOILERPLATE_NAMES.add("_register_onexit_function");
        BOILERPLATE_NAMES.add("_initialize_onexit_table");
    }

    private int getInstructionCount(Function func) {
        int count = 0;
        InstructionIterator iter = currentProgram.getListing().getInstructions(func.getBody(), true);
        while (iter.hasNext()) {
            iter.next();
            count++;
        }
        return count;
    }

    @Override
    public void run() throws Exception {
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);

        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        ConsoleTaskMonitor monitor = new ConsoleTaskMonitor();

        println("[*] Starting headless decompilation with complexity filtering...");

        JsonObject rootJson = new JsonObject();

        for (Function func : functions) {
            String funcName = func.getName();
            String entryPoint = func.getEntryPoint().toString();

            if (func.isThunk() || func.isExternal()) {
                continue;
            }

            if (BOILERPLATE_NAMES.contains(funcName) || 
                funcName.startsWith("__") || 
                funcName.startsWith("_guard_") || 
                funcName.startsWith("tc_")) {
                println("[~] Skipping boilerplate name: " + funcName);
                continue;
            }

            DecompileResults results = decompiler.decompileFunction(func, 30, monitor);

            if (results != null && results.decompileCompleted()) {
                DecompiledFunction decompiledMarkup = results.getDecompiledFunction();
                String pseudoC = decompiledMarkup.getC();

                if (pseudoC == null || pseudoC.trim().length() < 35) {
                    println("[~] Skipping visually empty/trivial decompiled output: " + funcName);
                    continue;
                }

                JsonObject funcObj = new JsonObject();
                funcObj.addProperty("address", entryPoint);
                funcObj.addProperty("raw_c", pseudoC);
                
                rootJson.add(funcName, funcObj);
                int instrCount = getInstructionCount(func);
                println("[+] Decompiled: " + funcName + " (Instructions: " + instrCount + ")");
            } else {
                println("[-] Failed to decompile: " + funcName);
            }
        }

        String[] args = getScriptArgs();
        String outputPath = args.length > 0 ? args[0] : "decompiled_output.json";

        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        try (FileWriter file = new FileWriter(outputPath)) {
            gson.toJson(rootJson, file);
        } catch (IOException e) {
            println("[-] Error writing file: " + e.getMessage());
        }

        println("[*] Done! Decompilation saved to " + outputPath);
    }
}