package com.morova.onlab;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Controller {

    @Autowired
    LoadSimulatorManager loadSimulatorManager;

    @GetMapping
    @RequestMapping("/")
    public String index() {
        return loadSimulatorManager.hello();
    }

    @GetMapping
    @RequestMapping("/time")
    public void doTimeConsumingTask() {
        loadSimulatorManager.doTimeConsumingTask();
    }
}
