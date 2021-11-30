import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.*;
import java.net.*;

public class OTT {

    private Socket clienteSocket;
    private PrintWriter out;
    private BufferedReader in;

    public void startConn(String ip, int port) throws IOException {
        clienteSocket = new Socket(ip,port);
        out = new PrintWriter(clienteSocket.getOutputStream(),true);
        in = new BufferedReader(new InputStreamReader(clienteSocket.getInputStream()));
    }

    public String sendMessage(String msg) throws IOException {
        out.println(msg);
        return in.readLine();
    }

    public static void main(String[] args) throws IOException {
        OTT o = new OTT();
        o.startConn("127.0.0.1",9999);
        String resp = o.sendMessage("hello server");
        if (resp.equals("hello client")){
            System.out.println("True");
        }
        else{
            System.out.println("Error");
        }
    }
}
