function launchSpec(dataProvider)
{
    var ret = {
        commandLine: [ "python", "/opt/micall/micall_basespace.py" ],
        containerImageId: "docker.illumina.com/cfelab/micall",
        Options: [ "bsfs.enabled=true" ]
    };
    return ret;
}

// example multi-node launch spec
/*
function launchSpec(dataProvider)
{
    var ret = {
        nodes: []
    };
    
    ret.nodes.push({
        appSessionName: "Hello World 1",
        commandLine: [ "cat", "/illumina.txt" ],
        containerImageId: "basespace/demo",
        Options: [ "bsfs.enabled=true" ]
    });
    
    ret.nodes.push({
        appSessionName: "Hello World 2",
        commandLine: [ "cat", "/illumina.txt" ],
        containerImageId: "basespace/demo",
        Options: [ "bsfs.enabled=true" ]
    });
    
    return ret;
}
*/

/* 
function billingSpec(dataProvider) {
    return [
    {
        "Id" : "insert product ID here",
        "Quantity": 1.0
    }];
}
*/
