import static com.cloudbees.plugins.credentials.CredentialsScope.GLOBAL
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.SystemCredentialsProvider
import hudson.util.Secret
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl
import com.cloudbees.plugins.credentials.CredentialsStore
import jenkins.model.*
import hudson.util.Secret
import java.text.SimpleDateFormat

class Base{

    // geneating token for further processing
    def generateToken(username, password){
        String token = username + ":" + password

        return token.bytes.encodeBase64().toString();
    }

    // geneating date for further processing
    def getDate(){
        def date = new Date()
        def simpleDateFormat = new SimpleDateFormat("MM-dd-yyyy_HH:mm:ss")
        def date_time = simpleDateFormat.format(date)

        return date_time;
    }
}



def build(String username, String password) {

    def base = new Base();

    //String token = username + ":" + password
    def payload = base.generateToken(username, password);

    // println (payload)

    CredentialsStore credentialsStore = SystemCredentialsProvider.getInstance().getStore()
    //creating instance of credential store
    def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(com.cloudbees.plugins.credentials.common.StandardCredentials.class, Jenkins.instance)

    //checking user credential exists or not
    def instance = creds.findResult { it.id == username ? it : null }

    if(instance) {
        println "found credential of [${username}]"
        //updating user credential as user exists
        def result = credentialsStore.updateCredentials(Domain.global(), instance, 
            new StringCredentialsImpl(instance.scope, instance.id, instance.description, Secret.fromString(payload)))

        if (result) {
            println "secret updated for [${username}]" 
        } else {
            println "failed to change secret for [${username}]"
        }
    } else {
        println "could not find credential for [${username}]" 
        println "adding credential of [${username}] to the store" 
        //creating user credential if user is new to the job
        StringCredentialsImpl secretTextCredentials = new StringCredentialsImpl(GLOBAL, username, "${username}-${base.getDate()}", Secret.fromString(payload))
        credentialsStore.addCredentials(Domain.global(), secretTextCredentials)
    }
}

return this