import http from "k6/http";
import { check, sleep } from "k6";

export let options = {
    stages: [
        //{ duration: '1s', target: 70 },
        { duration: '15s', target: {{TARGET}} }
    ],
};

export default function () {
    var arr = ["1000kb","1000kba","1000kbb","1000kbc","1000kbd"];
    //var arr = ["10kb","10kba","10kbb","10kbc"];
    //var arr = ["10kb"];
    //var arr = ["1000kb"];
    var hd = ["x-webhook"]
    var url = "http://141.164.61.232:8080/v1/AUTH_7e49ba5247154b51be8bf681d4919627/test/" + arr[Math.floor(Math.random() * arr.length)];
    var params = {
        headers: {
            "x-webhook" : "http://10.233.9.13:8080",
            "X-Auth-Token": "gAAAAABgux5OJoOfOJIfpahs7HAlRqkRtt7aZx-WL-leizMLRW-GsZitGQmQ5QmYqQoHel_FcLyONQCKNrGkLgICb_5_ZLKceDOT28td9ez54XJViq7glDVdGheazBze_zZhCD3rCWNV6qrliPGLHeNd_wUVwzfZGRRKCje9EMO6uM6-cAljXCA"
        }
    }
    var params1 = {
        headers: {
            "X-Auth-Token": "gAAAAABgux5OJoOfOJIfpahs7HAlRqkRtt7aZx-WL-leizMLRW-GsZitGQmQ5QmYqQoHel_FcLyONQCKNrGkLgICb_5_ZLKceDOT28td9ez54XJViq7glDVdGheazBze_zZhCD3rCWNV6qrliPGLHeNd_wUVwzfZGRRKCje9EMO6uM6-cAljXCA"
        }
    }

    var res
    if(Math.floor(Math.random() * 2) == 0){
        res = http.get(url, params);
    }else{
        res = http.get(url, params1);
    }
    
    check(res, {
        "status was 200": (r) => r.status == 200
    });
    sleep(0.1)
};

