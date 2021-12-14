import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

public class OTTClient {

    public static void main(String[] args) throws IOException {

        String ip = "127.0.0.1";
        Socket clientSocket = new Socket(ip,8080);
        BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

        while(true){
            out.println("Client with IP " + ip + " connected to server on port 8080");
        }

    }

}
