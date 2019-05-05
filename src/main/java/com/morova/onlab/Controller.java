package com.morova.onlab;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Controller {

    @Autowired
    LoadSimulatorManager loadSimulatorManager;

    @GetMapping
    @RequestMapping("/time")
    public void doTimeConsumingTask() {
        loadSimulatorManager.doTimeConsumingTask();
    }

    @GetMapping
    @RequestMapping("/memory")
    public void doMemoryConsumingTask() {
        loadSimulatorManager.doMemoryConsumingTask();
    }

    @GetMapping
    @RequestMapping("/setPoolSize")
    public void setPoolSize(@RequestParam int poolSize) {
        loadSimulatorManager.setPoolSize(poolSize);
    }
}
