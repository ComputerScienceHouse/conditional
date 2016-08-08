import _ from "lodash";

export default class MemberUtil {
  static splitFreshmenUpperclassmen(memberIds) {
    let result = {
      freshmen: [],
      upperclassmen: []
    };

    memberIds.forEach(memberId => {
      if (memberId) {
        if (_.isNaN(memberId)) {
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
