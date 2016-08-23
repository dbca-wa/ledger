package dpaw.bpay;

import au.com.bpay.payments.crnvalidator.util.CRNGeneratorHelper;
import au.com.bpay.payments.crnvalidator.util.CRNGenerationException;

public class DPAWBPAYCrnGenerator {
    /**
     * Class to implement generation of BPAY CRN
     */
    private final CRNGeneratorHelper mCRNGeneratorHelper;
    
    /** Constructor **/
    public DPAWBPAYCrnGenerator (){
        mCRNGeneratorHelper = new CRNGeneratorHelper();
    }
    
    /** Method to generate BPAY CRN using MOD10V01 **/
    public String generateBPAYCrnWithMod10V01(String aCRNWithoutCD){
        try{
            return mCRNGeneratorHelper.generateCrn(aCRNWithoutCD, "MOD10V01");
        }
        catch (CRNGenerationException e){
            String errorCode = e.getCheckDigitErrorReturnCode();
            
            return errorCode;
        }
    }
}