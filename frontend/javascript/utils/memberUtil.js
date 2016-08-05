export default class MemberUtil {
  static splitFreshmenUpperclassmen(memberIds) {
    let result = {
      freshmen: [],
      upperclassmen: []
    };

    memberIds.forEach(memberId => {
      if (typeof memberId !== "undefined" &&
          memberId !== "" &&
          memberId !== null) {
        if (isNaN(memberId)) {
          // Upperclassman account
          result.upperclassmen.push(memberId);
        } else {
          // Numeric ID, freshman account
          result.freshmen.push(memberId);
        }
      }
    });

    return result;
  }
}
