export default class MemberUtil {
    static splitFreshmenUpperclassmen (memberIds) {
        let result = {
            "freshmen": [],
            "upperclassmen": []
        }
        
        memberIds.forEach((memberId) => {
            if (typeof memberId !== "undefined" && memberId !== "" && memberId !== null) {
                if (!isNaN(memberId)) {
                    // Numeric ID, freshman account
                    result.freshmen.push(memberId);
                } else {
                    // Upperclassman account
                    result.upperclassmen.push(memberId);
                }
            }
        });
        
        return result;
    }
}