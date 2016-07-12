package dpaw.bpay;

import au.com.bpay.payments.crnvalidator.util.CRNGeneratorHelper;
import au.com.bpay.payments.crnvalidator.util.CRNGenerationException;
/** required for ICRN generation **/
import java.math.BigDecimal;
import java.util.Date;

public class DPAWBPAYIcrnGenerator {
    /**
     * Class to implement generation of BPAY CRN
     */
    private final CRNGeneratorHelper mCRNGeneratorHelper;
    
    /** Constructor **/
    public DPAWBPAYIcrnGenerator (){
        mCRNGeneratorHelper = new CRNGeneratorHelper();
    }
    
    /** Method to generate BPAY iCRN using ICRNAMT **/
    public String generateBPAYIcrnAmt(String aCRNWithoutCD, BigDecimal amt){
        try{
            return mCRNGeneratorHelper.generateIcrn(aCRNWithoutCD, "ICRNAMT", amt, null);
        }
        catch (CRNGenerationException e){
            String errorCode = e.getCheckDigitErrorReturnCode();
            
            return errorCode;
        }
    }
    
    /** Method to generate BPAY iCRN using ICRNDATE **/
    public String generateBPAYIcrnDate(String aCRNWithoutCD, Date dueDate){
        try{
            return mCRNGeneratorHelper.generateIcrn(aCRNWithoutCD, "ICRNDATE", null, dueDate);
        }
        catch (CRNGenerationException e){
            String errorCode = e.getCheckDigitErrorReturnCode();
            
            return errorCode;
        }
    }
    
    /** Method to generate BPAY iCRN using ICRNAMTDATE **/
    public String generateBPAYIcrnAmtDate(String aCRNWithoutCD, BigDecimal amt, Date dueDate){
        try{
            return mCRNGeneratorHelper.generateIcrn(aCRNWithoutCD, "ICRNAMTDTE", amt, dueDate);
        }
        catch (CRNGenerationException e){
            String errorCode = e.getCheckDigitErrorReturnCode();
            
            return errorCode;
        }
    }
}