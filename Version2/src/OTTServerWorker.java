import java.io.*;
import java.net.*;
import java.util.*;

public class OTTServerWorker implements Runnable{

    private ServerSocket socketEnviar;
    private PrintWriter out;
    private BufferedReader in;

    public OTTServerWorker(ServerSocket serverSocket, Socket clientSocket) throws IOException {
        this.socketEnviar = serverSocket;
        clientSocket = socketEnviar.accept();
        this.out = new PrintWriter(clientSocket.getOutputStream(), true);
        this.in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
    }


    public void run() {
        try {
            while(true) {
                String greeting = in.readLine();
                if ("hello server".equals(greeting)) {
                    out.println("hello client");
                } else {
                    out.println("unrecognized greeting");
                }
            }
        }catch (IOException e){
            e.printStackTrace();
        }
    }


}
