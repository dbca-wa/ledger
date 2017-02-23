package dpaw.bpay;
import java.net.InetAddress;
import java.net.UnknownHostException;
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
        int port = 25333;
        if (args.length > 1){
            System.err.println("Usage is : BPAYEntryPoint.java <port>");
            System.exit(1);
        }
        else if(args.length == 1){
            port = Integer.parseInt(args[0]);
        }
        BPAYEntryPoint bpayEntry = new BPAYEntryPoint();
        GatewayServer gatewayServer = null;
        try{
            InetAddress host = InetAddress.getByName("0.0.0.0");
            gatewayServer = new GatewayServer(bpayEntry, port, 0, host, null, 0, 0, null );
            System.out.println( "GatewayServer for " + bpayEntry.getClass().getName() + " started on " + host.toString() + ":" + port );
        }
        catch (UnknownHostException e) {
            System.out.println( "exception occurred while constructing GatewayServer()." ); 
            e.printStackTrace();
        }
        gatewayServer.start();
    }
}
