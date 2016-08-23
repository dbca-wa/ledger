package dpaw.bpay;
import py4j.GatewayServer;

public class BPAYEntryPoint {
    private DPAWBPAYCrnGenerator crn;
    private DPAWBPAYIcrnGenerator icrn;
    
    public BPAYEntryPoint(){
        crn = new DPAWBPAYCrnGenerator();
        icrn = new DPAWBPAYIcrnGenerator();
    }
    /** Get the CRN object **/
    public DPAWBPAYCrnGenerator getCRN(){
        return crn;
    }
    /** Get the iCRN object **/
    public DPAWBPAYIcrnGenerator getiCRN(){
        return icrn;
    }
    
    public static void main(String[] args){
        BPAYEntryPoint bpayEntry = new BPAYEntryPoint();
        //GatewayServer gatewayServer = new GatewayServer(bpayEntry, 8006);
        GatewayServer gatewayServer = new GatewayServer(bpayEntry);
        gatewayServer.start();
        System.out.println("Gateway server started");
    }
}