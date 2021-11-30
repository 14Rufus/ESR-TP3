import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.*;
import java.util.*;

public class Node {

    private ServerSocket socketEnviar;
    private Socket socketReceber;
    private PrintWriter out;
    private BufferedReader in;


    public void start(int port) throws IOException {
        this.socketEnviar = new ServerSocket(port);
        this.socketReceber = socketEnviar.accept();
        this.out = new PrintWriter(socketReceber.getOutputStream(),true);
        this.in = new BufferedReader(new InputStreamReader(socketReceber.getInputStream()));
        String greeting = in.readLine();
        if ("hello server".equals(greeting)){
            out.println("hello client");
        }
        else{
            out.println("unrecognized greeting");
        }
    }

    public static void main(String[] args) throws IOException {
        Node n = new Node();
        n.start(9999);
    }

}
